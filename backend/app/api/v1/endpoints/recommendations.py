"""
Sentinel AI — Recommendation Engine REST Endpoints

Provides API routes for generating prioritized remediation recommendations,
inspecting supporting evidence telemetry, and fetching historical recommendation logs.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import RecommendationCategory, RecommendationPriority
from app.models.user import User
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["AI Remediation Recommendation Engine"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class GenerateRecommendationRequest(BaseModel):
    category: RecommendationCategory = Field(default=RecommendationCategory.VALIDATION_FAILURE)
    rca_id: uuid.UUID | None = None
    dataset_id: uuid.UUID | None = None


class RecommendationEvidenceResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    evidence_payload: dict[str, Any] | None = None
    weight: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    rca_id: uuid.UUID | None = None
    dataset_id: uuid.UUID | None = None
    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    description: str
    estimated_impact: str
    estimated_effort: str
    confidence_score: float
    priority_score: float
    suggested_next_steps: dict[str, Any] | None = None
    status: str
    execution_time_ms: float
    created_at: datetime.datetime
    evidences: list[RecommendationEvidenceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post("/generate", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED, summary="Generate AI Remediation Recommendation")
async def generate_recommendation(
    request: GenerateRecommendationRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Generate prioritized AI remediation recommendation for a target category or RCA."""
    svc = RecommendationService(db)
    return await svc.generate_recommendations(
        category=request.category,
        rca_id=request.rca_id,
        dataset_id=request.dataset_id,
    )


@router.get("/history", response_model=list[RecommendationResponse], summary="Get Recommendation Log")
async def get_recommendation_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated recommendation log ordered by priority_score desc."""
    svc = RecommendationService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/{id}", response_model=RecommendationResponse, summary="Get Recommendation Detail")
async def get_recommendation_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed remediation recommendation report by ID."""
    svc = RecommendationService(db)
    rec = await svc.get_by_id(id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation '{id}' not found",
        )
    return rec
