"""
Sentinel AI — Data Drift REST Endpoints

Provides API routes for triggering data drift detection runs, retrieving historical drift runs,
and viewing detailed per-column statistical drift reports.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import DetectorType, DriftSeverity, DriftStatus
from app.models.user import User
from app.services.drift_service import DriftService

router = APIRouter(tags=["Data Drift Engine"])


# ── Pydantic Request/Response Schemas ─────────────────────────────────────────
class DriftTriggerRequest(BaseModel):
    current_version_id: uuid.UUID
    baseline_version_id: uuid.UUID | None = None


class DriftResultResponse(BaseModel):
    id: uuid.UUID
    column_name: str
    column_type: str
    detector_type: DetectorType
    drift_detected: bool
    drift_score: float
    threshold: float
    severity: DriftSeverity
    explanation: str
    metrics_data: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class DriftRunResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    current_version_id: uuid.UUID
    baseline_version_id: uuid.UUID
    status: DriftStatus
    overall_drift_score: float
    drifted_columns_count: int
    total_columns_analyzed: int
    execution_time_ms: float
    summary: dict[str, Any] | None = None
    results: list[DriftResultResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post(
    "/datasets/{id}/drift",
    response_model=DriftRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger Data Drift Detection",
)
async def trigger_drift_detection(
    id: uuid.UUID,
    payload: DriftTriggerRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Trigger a Data Drift Detection Engine run comparing current vs baseline version."""
    svc = DriftService(db)
    try:
        drift_run = await svc.run_drift_detection(
            dataset_id=id,
            current_version_id=payload.current_version_id,
            baseline_version_id=payload.baseline_version_id,
        )
        return drift_run
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get(
    "/datasets/{id}/drift-history",
    response_model=list[DriftRunResponse],
    summary="Get Dataset Drift Run History",
)
async def get_dataset_drift_history(
    id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated historical drift detection runs for a dataset."""
    svc = DriftService(db)
    return await svc.get_dataset_drift_history(dataset_id=id, skip=skip, limit=limit)


@router.get(
    "/drift/{id}",
    response_model=DriftRunResponse,
    summary="Get Detailed Drift Run Report",
)
async def get_drift_run_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed per-column drift report by DriftRun ID."""
    svc = DriftService(db)
    run = await svc.get_drift_run(id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DriftRun '{id}' not found",
        )
    return run
