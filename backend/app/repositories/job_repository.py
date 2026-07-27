"""
Sentinel AI — Job Repository

Provides database access operations for background Job entities.
"""

import uuid
from typing import Any

from sqlalchemy import select, func

from app.models.enums import JobStatus
from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for Job background execution entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(Job, session)

    async def get_pending_or_queued_jobs(self, limit: int = 50) -> list[Job]:
        """Fetch pending or queued background jobs ordered by priority and creation time."""
        result = await self._session.execute(
            select(Job)
            .where(Job.status.in_([JobStatus.PENDING, JobStatus.QUEUED]))
            .order_by(Job.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_jobs_by_dataset(
        self, dataset_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Job], int]:
        """Fetch paginated background jobs associated with a dataset."""
        count_res = await self._session.execute(
            select(func.count()).select_from(Job).where(Job.dataset_id == dataset_id)
        )
        total = count_res.scalar_one()

        result = await self._session.execute(
            select(Job)
            .where(Job.dataset_id == dataset_id)
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_jobs_by_status(
        self, status: JobStatus, offset: int = 0, limit: int = 20
    ) -> tuple[list[Job], int]:
        """Fetch paginated jobs filtered by JobStatus."""
        count_res = await self._session.execute(
            select(func.count()).select_from(Job).where(Job.status == status)
        )
        total = count_res.scalar_one()

        result = await self._session.execute(
            select(Job)
            .where(Job.status == status)
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total
