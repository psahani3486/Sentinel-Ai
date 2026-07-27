"""
Sentinel AI — Forecasting Repositories

Repository layer for persisting, querying, and sorting ForecastRun and ForecastResult entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.forecasting import ForecastResult, ForecastRun
from app.repositories.base import BaseRepository


class ForecastRunRepository(BaseRepository[ForecastRun]):
    """Repository for managing ForecastRun entities."""

    def __init__(self, session) -> None:
        super().__init__(ForecastRun, session)

    async def get_by_id_with_results(self, run_id: uuid.UUID) -> ForecastRun | None:
        """Fetch ForecastRun by ID including results and dataset relationship."""
        stmt = (
            select(ForecastRun)
            .where(ForecastRun.id == run_id)
            .options(
                selectinload(ForecastRun.results),
                selectinload(ForecastRun.dataset),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[ForecastRun]:
        """Fetch paginated forecast runs ordered by created_at desc."""
        stmt = (
            select(ForecastRun)
            .options(selectinload(ForecastRun.results))
            .order_by(ForecastRun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class ForecastResultRepository(BaseRepository[ForecastResult]):
    """Repository for managing ForecastResult entities."""

    def __init__(self, session) -> None:
        super().__init__(ForecastResult, session)
