"""
Sentinel AI — Production Health Check Endpoints

Provides liveness, readiness, and deep system health probes for container orchestration
(Kubernetes, Render, Docker Compose, Upstash Redis, Neon PostgreSQL).
"""

import datetime
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.db.session import get_async_session

router = APIRouter(prefix="/health", tags=["Health Probes"])


@router.get("", summary="Basic Application Liveness Probe")
async def health_check() -> dict[str, Any]:
    """Basic liveness check — returns 200 OK if application process is running."""
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.get("/db", summary="Database Connectivity Check")
async def db_health_check(session: AsyncSession = Depends(get_async_session)) -> dict[str, Any]:
    """Readiness check — verifies database connectivity."""
    settings = get_settings()
    try:
        await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "database": db_status,
    }


@router.get("/readiness", summary="Cloud Readiness Probe")
async def readiness_probe(session: AsyncSession = Depends(get_async_session)) -> Response:
    """Readiness probe — returns HTTP 200 if database and app are ready to serve traffic."""
    try:
        await session.execute(text("SELECT 1"))
        return Response(content='{"status":"ready"}', media_type="application/json", status_code=status.HTTP_200_OK)
    except Exception:
        return Response(
            content='{"status":"not_ready"}',
            media_type="application/json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/liveness", summary="Cloud Liveness Probe")
async def liveness_probe() -> dict[str, str]:
    """Liveness probe — returns HTTP 200 if application process is alive."""
    return {
        "status": "alive",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
