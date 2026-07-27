"""
Sentinel AI — Drift Repositories

Repository layer for persisting and retrieving DriftRun and DriftResult records.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.drift import DriftResult, DriftRun
from app.repositories.base import BaseRepository


class DriftRunRepository(BaseRepository[DriftRun]):
    """Repository for managing DriftRun persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(DriftRun, session)

    async def get_by_id_with_results(self, drift_run_id: uuid.UUID) -> DriftRun | None:
        """Fetch DriftRun by ID eager loading detailed DriftResult records."""
        stmt = (
            select(DriftRun)
            .where(DriftRun.id == drift_run_id)
            .options(
                selectinload(DriftRun.results),
                selectinload(DriftRun.dataset),
                selectinload(DriftRun.current_version),
                selectinload(DriftRun.baseline_version),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history_by_dataset_id(
        self, dataset_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Sequence[DriftRun]:
        """Fetch paginated history of drift runs for a dataset."""
        stmt = (
            select(DriftRun)
            .where(DriftRun.dataset_id == dataset_id)
            .options(selectinload(DriftRun.results))
            .order_by(DriftRun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class DriftResultRepository(BaseRepository[DriftResult]):
    """Repository for managing DriftResult persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(DriftResult, session)
