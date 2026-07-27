"""
Sentinel AI — Workflow Service

Service layer managing workflow DAG execution, state transitions, and step run persistence.
"""

import datetime
import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WorkflowStepState, WorkflowType
from app.models.workflow import WorkflowRun, WorkflowStepRun
from app.repositories.workflow_repository import (
    WorkflowRunRepository,
    WorkflowStepRunRepository,
)
from app.workflows.base_workflow import WorkflowContext
from app.workflows.engine import WorkflowEngine
from app.workflows.reporter import WorkflowReporter

logger = logging.getLogger(__name__)


class WorkflowService:
    """Coordinates workflow DAG execution and database persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        run_repo: WorkflowRunRepository | None = None,
        step_repo: WorkflowStepRunRepository | None = None,
        engine: WorkflowEngine | None = None,
        reporter: WorkflowReporter | None = None,
    ) -> None:
        self._session = db_session
        self._run_repo = run_repo or WorkflowRunRepository(db_session)
        self._step_repo = step_repo or WorkflowStepRunRepository(db_session)
        self._engine = engine or WorkflowEngine()
        self._reporter = reporter or WorkflowReporter()

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

    async def run_workflow(
        self,
        workflow_type: WorkflowType,
        dataset_id: uuid.UUID | None = None,
        title: str = "Sentinel AI Workflow Execution",
        parameters: dict[str, Any] | None = None,
    ) -> WorkflowRun:
        """Execute workflow DAG and persist run and step execution entities."""
        context = WorkflowContext(
            workflow_type=workflow_type,
            dataset_id=dataset_id,
            title=title,
            parameters=parameters or {},
        )

        res = self._engine.run_workflow(context)

        now = datetime.datetime.now(datetime.timezone.utc)
        completed_cnt = sum(1 for s in res.step_outputs if s.state == WorkflowStepState.COMPLETED)
        failed_cnt = sum(1 for s in res.step_outputs if s.state == WorkflowStepState.FAILED)

        run_entity = WorkflowRun(
            dataset_id=dataset_id,
            workflow_type=workflow_type,
            state=res.state,
            title=res.title,
            total_steps=len(res.step_definitions),
            completed_steps=completed_cnt,
            failed_steps=failed_cnt,
            started_at=now,
            completed_at=now,
            execution_time_ms=sum(s.execution_time_ms for s in res.step_outputs),
            context_data=self._sanitize_dict(parameters or {}),
        )
        run_entity = await self._run_repo.create(run_entity)

        # Map step definitions to step outputs
        out_map = {out.step_name: out for out in res.step_outputs}

        for sdef in res.step_definitions:
            sout = out_map.get(sdef.step_name)
            s_state = sout.state if sout else WorkflowStepState.PENDING
            s_exec = sout.execution_time_ms if sout else 0.0
            s_logs = sout.logs if sout else ""
            s_outs = self._sanitize_dict(sout.outputs if sout else {})

            step_entity = WorkflowStepRun(
                workflow_run_id=run_entity.id,
                step_name=sdef.step_name,
                step_type=sdef.step_type,
                state=s_state,
                depends_on={"depends_on": sdef.depends_on},
                max_retries=sdef.max_retries,
                started_at=now,
                completed_at=now,
                execution_time_ms=s_exec,
                logs=s_logs,
                outputs=s_outs,
            )
            await self._step_repo.create(step_entity)

        logger.info("Executed Workflow Run '%s' -> Type: %s, State: %s",
                    run_entity.id, workflow_type.value, res.state.value)

        return await self._run_repo.get_by_id_with_steps(run_entity.id) or run_entity

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[WorkflowRun]:
        """Fetch paginated workflow run history."""
        return await self._run_repo.get_history(skip=skip, limit=limit)

    async def get_by_id(self, run_id: uuid.UUID) -> WorkflowRun | None:
        """Fetch workflow run by ID with steps."""
        return await self._run_repo.get_by_id_with_steps(run_id)

    async def get_steps(self, run_id: uuid.UUID) -> Sequence[WorkflowStepRun]:
        """Fetch step execution runs for a workflow run."""
        return await self._step_repo.get_by_workflow_run_id(run_id)
