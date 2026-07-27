"""
Sentinel AI — Platform Telemetry & Observability REST Endpoints

Provides API routes for inspecting internal platform metrics, subsystem health statuses,
and APM distributed trace waterfalls.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import MetricType, SpanStatus
from app.models.user import User
from app.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["Platform Telemetry, Metrics & Distributed Tracing"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class MetricSnapshotResponse(BaseModel):
    id: uuid.UUID
    metric_name: str
    metric_type: MetricType
    value: float
    unit: str
    labels: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class SpanResponse(BaseModel):
    id: uuid.UUID
    span_id: str
    trace_id_str: str
    parent_span_id: str | None = None
    name: str
    service_name: str
    status: SpanStatus
    duration_ms: float
    attributes: dict[str, Any] | None = None
    start_time: datetime.datetime
    end_time: datetime.datetime

    class Config:
        from_attributes = True


class TraceResponse(BaseModel):
    id: uuid.UUID
    trace_id: str
    name: str
    service_name: str
    duration_ms: float
    status: SpanStatus
    start_time: datetime.datetime
    end_time: datetime.datetime
    spans: list[SpanResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.get("/metrics", response_model=list[MetricSnapshotResponse], summary="Get Telemetry Metrics")
async def get_telemetry_metrics(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve internal platform metric snapshots."""
    svc = TelemetryService(db)
    return await svc.get_metrics()


@router.get("/health", summary="Get Subsystem Health Status")
async def get_telemetry_health(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve subsystem operational health status matrix."""
    svc = TelemetryService(db)
    return await svc.get_health()


@router.get("/traces", response_model=list[TraceResponse], summary="Get APM Distributed Traces")
async def get_telemetry_traces(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve recent APM distributed trace contexts."""
    svc = TelemetryService(db)
    return await svc.get_traces()


@router.get("/traces/{id}", response_model=TraceResponse, summary="Get APM Trace Detail")
async def get_telemetry_trace_detail(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed APM trace with span waterfall by string trace_id."""
    svc = TelemetryService(db)
    trace = await svc.get_trace_detail(id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{id}' not found",
        )
    return trace
