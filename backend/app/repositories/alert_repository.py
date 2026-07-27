"""
Sentinel AI — Alert Repositories

Repository layer for persisting, querying, deduplicating, and updating Alert and AlertOccurrence entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.alert import Alert, AlertOccurrence
from app.models.enums import AlertStatus
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Repository for managing Alert entities and deduplication lookups."""

    def __init__(self, session) -> None:
        super().__init__(Alert, session)

    async def get_by_id_with_relations(self, alert_id: uuid.UUID) -> Alert | None:
        """Fetch Alert by ID including occurrences, dataset, and user relationships."""
        stmt = (
            select(Alert)
            .where(Alert.id == alert_id)
            .options(
                selectinload(Alert.occurrences),
                selectinload(Alert.dataset),
                selectinload(Alert.acknowledged_by),
                selectinload(Alert.resolved_by),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_active_by_fingerprint(self, fingerprint: str) -> Alert | None:
        """Find active un-resolved alert matching target fingerprint (OPEN or ACKNOWLEDGED)."""
        stmt = (
            select(Alert)
            .where(
                Alert.fingerprint == fingerprint,
                Alert.status.in_([AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED]),
            )
            .order_by(Alert.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def get_open_alerts(self, skip: int = 0, limit: int = 50) -> Sequence[Alert]:
        """Fetch active OPEN or ACKNOWLEDGED alerts ordered by last_seen_at desc."""
        stmt = (
            select(Alert)
            .where(Alert.status.in_([AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED]))
            .options(selectinload(Alert.occurrences))
            .order_by(Alert.last_seen_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[Alert]:
        """Fetch paginated historical alerts ordered by created_at desc."""
        stmt = (
            select(Alert)
            .options(selectinload(Alert.occurrences))
            .order_by(Alert.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class AlertOccurrenceRepository(BaseRepository[AlertOccurrence]):
    """Repository for managing AlertOccurrence persistence."""

    def __init__(self, session) -> None:
        super().__init__(AlertOccurrence, session)
