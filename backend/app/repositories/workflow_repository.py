"""
Sentinel AI — Workflow Repositories

Repository layer for persisting, querying, and sorting WorkflowRun and WorkflowStepRun entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.workflow import WorkflowRun, WorkflowStepRun
from app.repositories.base import BaseRepository


class WorkflowRunRepository(BaseRepository[WorkflowRun]):
    """Repository for managing WorkflowRun entities."""

    def __init__(self, session) -> None:
        super().__init__(WorkflowRun, session)

    async def get_by_id_with_steps(self, run_id: uuid.UUID) -> WorkflowRun | None:
        """Fetch WorkflowRun by ID including step runs and dataset relationship."""
        stmt = (
            select(WorkflowRun)
            .where(WorkflowRun.id == run_id)
            .options(
                selectinload(WorkflowRun.step_runs),
                selectinload(WorkflowRun.dataset),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[WorkflowRun]:
        """Fetch paginated workflow runs ordered by created_at desc."""
        stmt = (
            select(WorkflowRun)
            .options(selectinload(WorkflowRun.step_runs))
            .order_by(WorkflowRun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class WorkflowStepRunRepository(BaseRepository[WorkflowStepRun]):
    """Repository for managing WorkflowStepRun entities."""

    def __init__(self, session) -> None:
        super().__init__(WorkflowStepRun, session)

    async def get_by_workflow_run_id(self, run_id: uuid.UUID) -> Sequence[WorkflowStepRun]:
        """Fetch step runs for a workflow run ordered by created_at asc."""
        stmt = (
            select(WorkflowStepRun)
            .where(WorkflowStepRun.workflow_run_id == run_id)
            .order_by(WorkflowStepRun.created_at.asc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()
