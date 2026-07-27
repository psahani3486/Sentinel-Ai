"""
Sentinel AI — Incident Repositories

Repository layer for persisting, querying, and sorting Incident and IncidentEvent entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.incident import Incident, IncidentEvent
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    """Repository for managing Incident entities."""

    def __init__(self, session) -> None:
        super().__init__(Incident, session)

    async def get_by_id_with_timeline(self, incident_id: uuid.UUID) -> Incident | None:
        """Fetch Incident by ID including timeline events and relationships."""
        stmt = (
            select(Incident)
            .where(Incident.id == incident_id)
            .options(
                selectinload(Incident.timeline_events),
                selectinload(Incident.dataset),
                selectinload(Incident.rca),
                selectinload(Incident.recommendation),
                selectinload(Incident.forecast),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[Incident]:
        """Fetch paginated incidents ordered by created_at desc."""
        stmt = (
            select(Incident)
            .options(selectinload(Incident.timeline_events))
            .order_by(Incident.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class IncidentEventRepository(BaseRepository[IncidentEvent]):
    """Repository for managing IncidentEvent entities."""

    def __init__(self, session) -> None:
        super().__init__(IncidentEvent, session)

    async def get_by_incident_id(self, incident_id: uuid.UUID) -> Sequence[IncidentEvent]:
        """Fetch timeline events by incident_id ordered by timestamp asc."""
        stmt = (
            select(IncidentEvent)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.timestamp.asc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()
