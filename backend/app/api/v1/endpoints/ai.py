"""
Sentinel AI — AI Root Cause Analysis REST Endpoints

Provides API routes for triggering AI root cause analysis reports,
viewing detailed evidence breakdowns, and retrieving historical RCA run logs.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import AnalysisStatus, AnalysisType, ValidationSeverity
from app.models.user import User
from app.services.root_cause_service import RootCauseService

router = APIRouter(prefix="/analysis", tags=["AI Root Cause Analysis Engine"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class TriggerAnalysisRequest(BaseModel):
    analysis_type: AnalysisType = Field(default=AnalysisType.VALIDATION_FAILURE)
    target_entity_type: str = Field(default="validation_run")
    target_entity_id: str = Field(...)
    dataset_id: uuid.UUID | None = None


class AnalysisEvidenceResponse(BaseModel):
    id: uuid.UUID
    evidence_type: str
    title: str
    description: str
    evidence_payload: dict[str, Any] | None = None
    weight: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class RootCauseAnalysisResponse(BaseModel):
    id: uuid.UUID
    analysis_type: AnalysisType
    target_entity_type: str
    target_entity_id: str
    dataset_id: uuid.UUID | None = None
    summary: str
    probable_root_cause: str
    confidence_score: float
    severity: ValidationSeverity
    affected_components: dict[str, Any] | None = None
    recommended_actions: dict[str, Any] | None = None
    status: AnalysisStatus
    execution_time_ms: float
    llm_provider_name: str
    created_at: datetime.datetime
    evidences: list[AnalysisEvidenceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post("/root-cause", response_model=RootCauseAnalysisResponse, status_code=status.HTTP_201_CREATED, summary="Trigger AI Root Cause Analysis")
async def trigger_root_cause_analysis(
    request: TriggerAnalysisRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Trigger hybrid AI root cause analysis for target entity."""
    svc = RootCauseService(db)
    return await svc.run_root_cause_analysis(
        analysis_type=request.analysis_type,
        target_entity_type=request.target_entity_type,
        target_entity_id=request.target_entity_id,
        dataset_id=request.dataset_id,
    )


@router.get("/history", response_model=list[RootCauseAnalysisResponse], summary="Get RCA Run History")
async def get_analysis_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated historical AI RCA report log."""
    svc = RootCauseService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/{id}", response_model=RootCauseAnalysisResponse, summary="Get RCA Report Detail")
async def get_analysis_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed AI Root Cause Analysis report by ID."""
    svc = RootCauseService(db)
    report = await svc.get_by_id(id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{id}' not found",
        )
    return report
