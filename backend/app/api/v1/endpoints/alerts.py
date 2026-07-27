"""
Sentinel AI — Alert REST Endpoints

Provides API routes for viewing active incident alerts, acknowledging/resolving alerts,
and inspecting historical incident occurrences.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import AlertSeverity, AlertStatus, AlertType
from app.models.user import User
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerting Engine"])


# ── Pydantic Response Schemas ──────────────────────────────────────────────────
class AlertOccurrenceResponse(BaseModel):
    id: uuid.UUID
    severity: AlertSeverity
    message: str
    event_payload: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: uuid.UUID
    fingerprint: str
    dataset_id: uuid.UUID | None = None
    alert_type: AlertType
    status: AlertStatus
    severity: AlertSeverity
    title: str
    description: str
    occurrence_count: int
    first_seen_at: datetime.datetime
    last_seen_at: datetime.datetime
    acknowledged_at: datetime.datetime | None = None
    acknowledged_by_id: uuid.UUID | None = None
    resolved_at: datetime.datetime | None = None
    resolved_by_id: uuid.UUID | None = None
    alert_metadata: dict[str, Any] | None = None
    occurrences: list[AlertOccurrenceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.get("", response_model=list[AlertResponse], summary="List All Alerts")
async def list_alerts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated list of all incident alerts."""
    svc = AlertService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/open", response_model=list[AlertResponse], summary="Get Open & Acknowledged Alerts")
async def get_open_alerts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve active OPEN and ACKNOWLEDGED alerts ordered by last_seen_at."""
    svc = AlertService(db)
    return await svc.get_open_alerts(skip=skip, limit=limit)


@router.get("/history", response_model=list[AlertResponse], summary="Get Historical Alerts Log")
async def get_alert_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve historical alert log ordered by created_at."""
    svc = AlertService(db)
    return await svc.get_history(skip=skip, limit=limit)


@router.get("/{id}", response_model=AlertResponse, summary="Get Alert Incident Detail")
async def get_alert_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed alert incident report by Alert ID."""
    svc = AlertService(db)
    alert = await svc.get_by_id(id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{id}' not found",
        )
    return alert


@router.post("/{id}/acknowledge", response_model=AlertResponse, summary="Acknowledge Alert")
async def acknowledge_alert(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Acknowledge an open incident alert."""
    svc = AlertService(db)
    try:
        return await svc.acknowledge_alert(id, user_id=current_user.id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/{id}/resolve", response_model=AlertResponse, summary="Resolve Alert")
async def resolve_alert(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Resolve an incident alert."""
    svc = AlertService(db)
    try:
        return await svc.resolve_alert(id, user_id=current_user.id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
