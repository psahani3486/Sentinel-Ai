"""
Sentinel AI — Plugin Orchestration REST Endpoints

Provides API routes for inspecting local extension plugins,
toggling lifecycle enable/disable states, and auditing permissions.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import PluginStatus, PluginType
from app.models.user import User
from app.services.plugin_service import PluginService

router = APIRouter(prefix="/plugins", tags=["Enterprise Plugin & Extension SDK"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class PluginInstallationResponse(BaseModel):
    id: uuid.UUID
    installed_at: datetime.datetime
    installed_by: str
    is_enabled: bool
    configuration: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class PluginResponse(BaseModel):
    id: uuid.UUID
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    status: PluginStatus
    entry_point: str
    minimum_platform_version: str
    permissions: dict[str, Any] | None = None
    manifest_data: dict[str, Any] | None = None
    created_at: datetime.datetime
    installations: list[PluginInstallationResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.get("", response_model=list[PluginResponse], summary="Get All Plugins")
async def get_plugins(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve list of discovered local extension plugins."""
    svc = PluginService(db)
    return await svc.get_all()


@router.get("/{id}", response_model=PluginResponse, summary="Get Plugin Detail")
async def get_plugin_detail(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed plugin metadata by string plugin_id."""
    svc = PluginService(db)
    plugin = await svc.get_by_id(id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{id}' not found",
        )
    return plugin


@router.post("/{id}/enable", response_model=PluginResponse, summary="Enable Plugin")
async def enable_plugin(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Enable an extension plugin."""
    svc = PluginService(db)
    try:
        return await svc.enable_plugin(id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/{id}/disable", response_model=PluginResponse, summary="Disable Plugin")
async def disable_plugin(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Disable an extension plugin."""
    svc = PluginService(db)
    try:
        return await svc.disable_plugin(id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/reload", response_model=list[PluginResponse], summary="Reload Local Plugins")
async def reload_plugins(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Rescan local directories and reload plugins."""
    svc = PluginService(db)
    return await svc.reload_plugins()
