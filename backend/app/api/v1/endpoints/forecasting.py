"""
Sentinel AI — Predictive Observability & Risk Forecasting REST Endpoints

Provides API routes for triggering statistical metric forecasting models,
inspecting confidence intervals, and fetching historical forecast logs.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import ForecastType, RiskLevel, TrendDirection
from app.models.user import User
from app.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecast", tags=["Predictive Observability & Risk Forecasting Engine"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class RunForecastRequest(BaseModel):
    forecast_type: ForecastType = Field(default=ForecastType.QUALITY_SCORE_TREND)
    dataset_id: uuid.UUID | None = None
    horizon_days: int = Field(default=7, ge=1, le=90)
    historical_series: list[float] | None = None


class ForecastResultResponse(BaseModel):
    id: uuid.UUID
    target_metric: str
    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    trend_direction: TrendDirection
    risk_level: RiskLevel
    explanation: str
    preventive_actions: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ForecastRunResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    forecast_type: ForecastType
    algorithm_name: str
    forecast_horizon_days: int
    overall_risk_level: RiskLevel
    summary: str
    execution_time_ms: float
    status: str
    created_at: datetime.datetime
    results: list[ForecastResultResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post("/run", response_model=ForecastRunResponse, status_code=status.HTTP_201_CREATED, summary="Run Predictive Observability Forecast")
async def run_forecast(
    request: RunForecastRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Execute predictive forecasting strategy against platform telemetry time series."""
    svc = ForecastService(db)
    return await svc.run_forecast(
        forecast_type=request.forecast_type,
        dataset_id=request.dataset_id,
        horizon_days=request.horizon_days,
        historical_series=request.historical_series,
    )


@router.get("/history", response_model=list[ForecastRunResponse], summary="Get Forecast History")
async def get_forecast_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated predictive forecast log."""
    svc = ForecastService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/{id}", response_model=ForecastRunResponse, summary="Get Forecast Detail")
async def get_forecast_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed predictive forecast report by ID."""
    svc = ForecastService(db)
    run = await svc.get_by_id(id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Forecast run '{id}' not found",
        )
    return run
