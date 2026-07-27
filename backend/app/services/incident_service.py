"""
Sentinel AI — Incident Service

Service layer managing multi-signal telemetry correlation, chronological event sorting,
and incident report persistence.
"""

import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.incidents.base_correlator import IncidentContext
from app.incidents.engine import IncidentEngine
from app.incidents.reporter import IncidentReporter
from app.models.enums import IncidentSeverity
from app.models.incident import Incident, IncidentEvent
from app.repositories.incident_repository import (
    IncidentEventRepository,
    IncidentRepository,
)

logger = logging.getLogger(__name__)


class IncidentService:
    """Coordinates telemetry signal correlation and incident persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        incident_repo: IncidentRepository | None = None,
        event_repo: IncidentEventRepository | None = None,
        engine: IncidentEngine | None = None,
        reporter: IncidentReporter | None = None,
    ) -> None:
        self._session = db_session
        self._incident_repo = incident_repo or IncidentRepository(db_session)
        self._event_repo = event_repo or IncidentEventRepository(db_session)
        self._engine = engine or IncidentEngine()
        self._reporter = reporter or IncidentReporter()

    def _sanitize_dict(self, d: dict[str, Any]) -> dict[str, Any]:
        """Convert non-JSON serializable objects into strings for JSON storage."""
        sanitized = {}
        for k, v in d.items():
            if isinstance(v, uuid.UUID):
                sanitized[k] = str(v)
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    async def create_incident(
        self,
        title: str,
        dataset_id: uuid.UUID | None = None,
        severity: IncidentSeverity = IncidentSeverity.HIGH,
        telemetry_signals: dict[str, Any] | None = None,
    ) -> Incident:
        """Correlate telemetry signals, build unified incident, and persist timeline."""
        context = IncidentContext(
            dataset_id=dataset_id,
            title=title,
            severity=severity,
            telemetry_signals=telemetry_signals or {},
        )

        res = self._engine.create_incident(context)

        incident_entity = Incident(
            dataset_id=dataset_id,
            title=res.title,
            severity=res.severity,
            status=res.status,
            summary=res.summary,
            root_cause_summary=res.root_cause_summary,
            recommendations_summary=res.recommendations_summary,
            forecast_summary=res.forecast_summary,
            related_datasets={"datasets": res.related_datasets},
            related_jobs={"jobs": res.related_jobs},
            related_alerts={"alerts": res.related_alerts},
        )
        incident_entity = await self._incident_repo.create(incident_entity)

        for event in res.timeline_events:
            clean_payload = self._sanitize_dict(event.payload)
            event_entity = IncidentEvent(
                incident_id=incident_entity.id,
                timestamp=event.timestamp,
                event_type=event.event_type,
                severity=event.severity,
                description=event.description,
                evidence_link=event.evidence_link,
                payload=clean_payload,
            )
            await self._event_repo.create(event_entity)

        logger.info("Created Incident '%s' -> Title: '%s', Events: %d",
                    incident_entity.id, title, len(res.timeline_events))

        return await self._incident_repo.get_by_id_with_timeline(incident_entity.id) or incident_entity

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[Incident]:
        """Fetch paginated incident history."""
        return await self._incident_repo.get_history(skip=skip, limit=limit)

    async def get_by_id(self, incident_id: uuid.UUID) -> Incident | None:
        """Fetch incident workspace by ID with timeline."""
        return await self._incident_repo.get_by_id_with_timeline(incident_id)

    async def get_timeline(self, incident_id: uuid.UUID) -> Sequence[IncidentEvent]:
        """Fetch timeline events for an incident ordered by timestamp asc."""
        return await self._event_repo.get_by_incident_id(incident_id)
