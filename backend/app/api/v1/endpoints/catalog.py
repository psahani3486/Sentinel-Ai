"""
Sentinel AI — Data Catalog & Governance REST Endpoints

Provides API routes for searching metadata catalog assets, querying lineage DAG graphs,
browsing business glossary terms, and auditing governance compliance policies.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import AssetType, DataSensitivity, LifecycleStatus
from app.models.user import User
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/catalog", tags=["Enterprise Data Catalog, Lineage & Governance Platform"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class CatalogLineageResponse(BaseModel):
    id: uuid.UUID
    source_asset_id: uuid.UUID
    target_asset_id: uuid.UUID
    relationship_type: str
    lineage_dag: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class CatalogAssetResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    name: str
    asset_type: AssetType
    domain: str
    owner: str
    steward: str
    business_description: str
    technical_description: str
    sensitivity: DataSensitivity
    retention_period_days: int
    lifecycle_status: LifecycleStatus
    tags: dict[str, Any] | None = None
    classifications: dict[str, Any] | None = None
    created_at: datetime.datetime
    outgoing_lineages: list[CatalogLineageResponse] = Field(default_factory=list)
    incoming_lineages: list[CatalogLineageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class GlossaryTermResponse(BaseModel):
    id: uuid.UUID
    term: str
    definition: str
    domain: str
    related_assets: dict[str, Any] | None = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class GovernancePolicyResponse(BaseModel):
    id: uuid.UUID
    policy_name: str
    category: str
    rules_definition: dict[str, Any] | None = None
    compliance_status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.get("/assets", response_model=list[CatalogAssetResponse], summary="Get Catalog Assets")
async def get_catalog_assets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve paginated metadata catalog assets."""
    svc = CatalogService(db)
    return await svc.get_assets(skip=skip, limit=limit)


@router.get("/assets/{id}", response_model=CatalogAssetResponse, summary="Get Catalog Asset Detail")
async def get_catalog_asset_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed catalog asset metadata by ID."""
    svc = CatalogService(db)
    asset = await svc.get_asset_detail(id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog asset '{id}' not found",
        )
    return asset


@router.get("/lineage/{id}", response_model=list[CatalogLineageResponse], summary="Get Asset Lineage DAG")
async def get_asset_lineage(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve lineage DAG edges for a catalog asset."""
    svc = CatalogService(db)
    return await svc.get_lineage(id)


@router.get("/glossary", response_model=list[GlossaryTermResponse], summary="Get Business Glossary")
async def get_business_glossary(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve business glossary terms."""
    svc = CatalogService(db)
    return await svc.get_glossary()


@router.get("/policies", response_model=list[GovernancePolicyResponse], summary="Get Governance Policies")
async def get_governance_policies(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve governance compliance policies."""
    svc = CatalogService(db)
    return await svc.get_policies()
