"""
Sentinel AI — Unified Incident Workspace REST Endpoints

Provides API routes for creating correlated incident investigation workspaces,
querying chronological event timelines, and inspecting signal evidence.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import IncidentEventType, IncidentSeverity, IncidentStatus
from app.models.user import User
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Unified Incident Investigation Workspace Engine"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class CreateIncidentRequest(BaseModel):
    title: str = Field(default="Critical Data Quality SLA Breach")
    dataset_id: uuid.UUID | None = None
    severity: IncidentSeverity = Field(default=IncidentSeverity.HIGH)
    telemetry_signals: dict[str, Any] | None = None


class IncidentEventResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime.datetime
    event_type: IncidentEventType
    severity: IncidentSeverity
    description: str
    evidence_link: str | None = None
    payload: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    rca_id: uuid.UUID | None = None
    recommendation_id: uuid.UUID | None = None
    forecast_id: uuid.UUID | None = None
    title: str
    severity: IncidentSeverity
    status: IncidentStatus
    summary: str
    root_cause_summary: str | None = None
    recommendations_summary: str | None = None
    forecast_summary: str | None = None
    related_datasets: dict[str, Any] | None = None
    related_jobs: dict[str, Any] | None = None
    related_alerts: dict[str, Any] | None = None
    resolved_at: datetime.datetime | None = None
    created_at: datetime.datetime
    timeline_events: list[IncidentEventResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post("/create", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, summary="Create Correlated Incident Workspace")
async def create_incident(
    request: CreateIncidentRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Correlate platform telemetry signals into a single unified incident workspace."""
    svc = IncidentService(db)
    return await svc.create_incident(
        title=request.title,
        dataset_id=request.dataset_id,
        severity=request.severity,
        telemetry_signals=request.telemetry_signals,
    )


@router.get("", response_model=list[IncidentResponse], summary="Get Incident Log")
async def get_incidents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated incident workspace log."""
    svc = IncidentService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/{id}", response_model=IncidentResponse, summary="Get Incident Detail")
async def get_incident_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed incident workspace by ID."""
    svc = IncidentService(db)
    inc = await svc.get_by_id(id)
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{id}' not found",
        )
    return inc


@router.get("/{id}/timeline", response_model=list[IncidentEventResponse], summary="Get Incident Timeline Events")
async def get_incident_timeline(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve chronological timeline events for an incident."""
    svc = IncidentService(db)
    return await svc.get_timeline(id)
