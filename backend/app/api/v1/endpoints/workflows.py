"""
Sentinel AI — Workflow Orchestration REST Endpoints

Provides API routes for triggering DAG workflow execution pipelines,
inspecting step execution states, and fetching execution logs.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import WorkflowState, WorkflowStepState, WorkflowType
from app.models.user import User
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Enterprise Workflow Orchestration Engine"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class RunWorkflowRequest(BaseModel):
    workflow_type: WorkflowType = Field(default=WorkflowType.END_TO_END_INVESTIGATION)
    dataset_id: uuid.UUID | None = None
    title: str = Field(default="Sentinel AI Workflow Execution")
    parameters: dict[str, Any] | None = None


class WorkflowStepRunResponse(BaseModel):
    id: uuid.UUID
    step_name: str
    step_type: str
    state: WorkflowStepState
    depends_on: dict[str, Any] | None = None
    retry_count: int
    max_retries: int
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None
    execution_time_ms: float
    logs: str | None = None
    outputs: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class WorkflowRunResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    workflow_type: WorkflowType
    state: WorkflowState
    title: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None
    execution_time_ms: float
    context_data: dict[str, Any] | None = None
    created_at: datetime.datetime
    step_runs: list[WorkflowStepRunResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post("/run", response_model=WorkflowRunResponse, status_code=status.HTTP_201_CREATED, summary="Run Workflow Execution DAG")
async def run_workflow(
    request: RunWorkflowRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Trigger execution of a built-in workflow orchestration DAG pipeline."""
    svc = WorkflowService(db)
    return await svc.run_workflow(
        workflow_type=request.workflow_type,
        dataset_id=request.dataset_id,
        title=request.title,
        parameters=request.parameters,
    )


@router.get("", response_model=list[WorkflowRunResponse], summary="Get Workflow Execution Log")
async def get_workflows(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated workflow execution log."""
    svc = WorkflowService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/{id}", response_model=WorkflowRunResponse, summary="Get Workflow Run Detail")
async def get_workflow_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed workflow execution run by ID."""
    svc = WorkflowService(db)
    wf = await svc.get_by_id(id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow run '{id}' not found",
        )
    return wf


@router.get("/{id}/steps", response_model=list[WorkflowStepRunResponse], summary="Get Workflow Step Executions")
async def get_workflow_steps(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve step execution runs for a workflow run."""
    svc = WorkflowService(db)
    return await svc.get_steps(id)
