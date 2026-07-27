"""
Sentinel AI — Alert Service

Service layer managing alert evaluation, fingerprint deduplication, severity escalation,
state machine transitions (acknowledge/resolve), and WebSocket event broadcasting.
"""

import datetime
import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.alert_engine.engine import AlertEngine
from app.alert_engine.reporter import AlertReporter
from app.events.event_bus import EventBusInterface, get_event_bus
from app.events.events import AlertCreatedEvent, AlertUpdatedEvent
from app.models.alert import Alert, AlertOccurrence
from app.models.enums import AlertStatus
from app.repositories.alert_repository import AlertOccurrenceRepository, AlertRepository

logger = logging.getLogger(__name__)


class AlertService:
    """Coordinates automated alert generation, deduplication, escalation, and lifecycle state management."""

    def __init__(
        self,
        db_session: AsyncSession,
        alert_repo: AlertRepository | None = None,
        occurrence_repo: AlertOccurrenceRepository | None = None,
        engine: AlertEngine | None = None,
        reporter: AlertReporter | None = None,
        event_bus: EventBusInterface | None = None,
    ) -> None:
        self._session = db_session
        self._alert_repo = alert_repo or AlertRepository(db_session)
        self._occurrence_repo = occurrence_repo or AlertOccurrenceRepository(db_session)
        self._engine = engine or AlertEngine()
        self._reporter = reporter or AlertReporter()
        self._event_bus = event_bus or get_event_bus()

    def _sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Convert non-JSON serializable objects (such as UUIDs) into strings for JSON storage."""
        sanitized = {}
        for k, v in payload.items():
            if isinstance(v, uuid.UUID):
                sanitized[k] = str(v)
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_payload(v)
            else:
                sanitized[k] = v
        return sanitized

    async def process_event(self, event_payload: dict[str, Any]) -> list[Alert]:
        """
        Evaluate event payload, apply fingerprint deduplication and escalation policy,
        persist Alert & AlertOccurrence entities, and broadcast WebSocket events.
        """
        clean_payload = self._sanitize_payload(event_payload)
        candidates = self._engine.process_event_payload(clean_payload)
        processed_alerts: list[Alert] = []

        for cand in candidates:
            fp = cand.generate_fingerprint()
            active_alert = await self._alert_repo.get_active_by_fingerprint(fp)

            now = datetime.datetime.now(datetime.timezone.utc)

            if active_alert:
                # ── Deduplication Flow ───────────────────────────────────────
                new_count = active_alert.occurrence_count + 1
                escalated_sev = self._engine.calculate_escalated_severity(active_alert.severity, new_count)

                active_alert = await self._alert_repo.update(
                    active_alert,
                    {
                        "occurrence_count": new_count,
                        "last_seen_at": now,
                        "severity": escalated_sev,
                    },
                )

                # Persist occurrence history
                occ = AlertOccurrence(
                    alert_id=active_alert.id,
                    severity=cand.severity,
                    message=cand.description,
                    event_payload=clean_payload,
                )
                await self._occurrence_repo.create(occ)

                logger.info("Deduplicated Alert '%s' -> Count: %d, Severity: %s",
                            active_alert.id, new_count, escalated_sev.value)

                await self._event_bus.publish(
                    AlertUpdatedEvent(
                        alert_id=active_alert.id,
                        alert_type=active_alert.alert_type,
                        status=active_alert.status,
                        severity=active_alert.severity,
                        title=active_alert.title,
                        description=active_alert.description,
                        occurrence_count=active_alert.occurrence_count,
                        dataset_id=active_alert.dataset_id,
                        metadata=active_alert.alert_metadata or {},
                    )
                )
                processed_alerts.append(active_alert)

            else:
                # ── New Alert Flow ───────────────────────────────────────────
                alert_entity = Alert(
                    fingerprint=fp,
                    dataset_id=cand.dataset_id,
                    alert_type=cand.alert_type,
                    status=AlertStatus.OPEN,
                    severity=cand.severity,
                    title=cand.title,
                    description=cand.description,
                    occurrence_count=1,
                    first_seen_at=now,
                    last_seen_at=now,
                    alert_metadata=cand.metadata,
                )
                alert_entity = await self._alert_repo.create(alert_entity)

                occ = AlertOccurrence(
                    alert_id=alert_entity.id,
                    severity=cand.severity,
                    message=cand.description,
                    event_payload=clean_payload,
                )
                await self._occurrence_repo.create(occ)

                logger.info("Created New Incident Alert '%s' -> Type: %s, Severity: %s",
                            alert_entity.id, cand.alert_type.value, cand.severity.value)

                await self._event_bus.publish(
                    AlertCreatedEvent(
                        alert_id=alert_entity.id,
                        alert_type=alert_entity.alert_type,
                        status=alert_entity.status,
                        severity=alert_entity.severity,
                        title=alert_entity.title,
                        description=alert_entity.description,
                        occurrence_count=1,
                        dataset_id=alert_entity.dataset_id,
                        metadata=alert_entity.alert_metadata or {},
                    )
                )
                processed_alerts.append(alert_entity)

        return processed_alerts

    async def acknowledge_alert(self, alert_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Alert:
        """Transition alert status to ACKNOWLEDGED."""
        alert = await self._alert_repo.get_by_id(alert_id)
        if not alert:
            raise ValueError(f"Alert '{alert_id}' not found")

        now = datetime.datetime.now(datetime.timezone.utc)
        updated = await self._alert_repo.update(
            alert,
            {
                "status": AlertStatus.ACKNOWLEDGED,
                "acknowledged_at": now,
                "acknowledged_by_id": user_id,
            },
        )

        await self._event_bus.publish(
            AlertUpdatedEvent(
                alert_id=updated.id,
                alert_type=updated.alert_type,
                status=updated.status,
                severity=updated.severity,
                title=updated.title,
                description=updated.description,
                occurrence_count=updated.occurrence_count,
                dataset_id=updated.dataset_id,
                metadata=updated.alert_metadata or {},
            )
        )
        return await self._alert_repo.get_by_id_with_relations(updated.id) or updated

    async def resolve_alert(self, alert_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Alert:
        """Transition alert status to RESOLVED."""
        alert = await self._alert_repo.get_by_id(alert_id)
        if not alert:
            raise ValueError(f"Alert '{alert_id}' not found")

        now = datetime.datetime.now(datetime.timezone.utc)
        updated = await self._alert_repo.update(
            alert,
            {
                "status": AlertStatus.RESOLVED,
                "resolved_at": now,
                "resolved_by_id": user_id,
            },
        )

        await self._event_bus.publish(
            AlertUpdatedEvent(
                alert_id=updated.id,
                alert_type=updated.alert_type,
                status=updated.status,
                severity=updated.severity,
                title=updated.title,
                description=updated.description,
                occurrence_count=updated.occurrence_count,
                dataset_id=updated.dataset_id,
                metadata=updated.alert_metadata or {},
            )
        )
        return await self._alert_repo.get_by_id_with_relations(updated.id) or updated

    async def get_open_alerts(self, skip: int = 0, limit: int = 50) -> Sequence[Alert]:
        """Fetch active OPEN or ACKNOWLEDGED alerts."""
        return await self._alert_repo.get_open_alerts(skip=skip, limit=limit)

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[Alert]:
        """Fetch paginated historical alerts."""
        return await self._alert_repo.get_history(skip=skip, limit=limit)

    async def get_by_id(self, alert_id: uuid.UUID) -> Alert | None:
        """Fetch alert by ID including occurrences."""
        return await self._alert_repo.get_by_id_with_relations(alert_id)
