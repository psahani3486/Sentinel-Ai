"""
Sentinel AI — API v1 Router

Aggregates all v1 endpoint routers into a single router
that gets mounted at /api/v1 by the FastAPI app.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    alerts,
    auth,
    catalog,
    datasets,
    drift,
    forecasting,
    health,
    incidents,
    plugins,
    policies,
    recommendations,
    telemetry,
    users,
    validations,
    websocket,
    workflows,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(datasets.router)
api_v1_router.include_router(validations.router)
api_v1_router.include_router(websocket.router)
api_v1_router.include_router(drift.router)
api_v1_router.include_router(alerts.router)
api_v1_router.include_router(ai.router)
api_v1_router.include_router(recommendations.router)
api_v1_router.include_router(forecasting.router)
api_v1_router.include_router(incidents.router)
api_v1_router.include_router(workflows.router)
api_v1_router.include_router(plugins.router)
api_v1_router.include_router(catalog.router)
api_v1_router.include_router(telemetry.router)
api_v1_router.include_router(policies.router)
