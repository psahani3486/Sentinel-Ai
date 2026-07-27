"""
Sentinel AI — Catalog Repositories

Repository layer for persisting, querying, and updating CatalogAsset,
CatalogLineage, GlossaryTerm, and GovernancePolicy entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.catalog import CatalogAsset, CatalogLineage, GlossaryTerm, GovernancePolicy
from app.repositories.base import BaseRepository


class CatalogAssetRepository(BaseRepository[CatalogAsset]):
    """Repository for managing CatalogAsset entities."""

    def __init__(self, session) -> None:
        super().__init__(CatalogAsset, session)

    async def get_by_id_with_lineage(self, asset_id: uuid.UUID) -> CatalogAsset | None:
        """Fetch CatalogAsset by ID including incoming and outgoing lineages."""
        stmt = (
            select(CatalogAsset)
            .where(CatalogAsset.id == asset_id)
            .options(
                selectinload(CatalogAsset.outgoing_lineages),
                selectinload(CatalogAsset.incoming_lineages),
                selectinload(CatalogAsset.dataset),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all_assets(self, skip: int = 0, limit: int = 50) -> Sequence[CatalogAsset]:
        """Fetch paginated catalog assets ordered by name asc."""
        stmt = (
            select(CatalogAsset)
            .options(
                selectinload(CatalogAsset.outgoing_lineages),
                selectinload(CatalogAsset.incoming_lineages),
            )
            .order_by(CatalogAsset.name.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class CatalogLineageRepository(BaseRepository[CatalogLineage]):
    """Repository for managing CatalogLineage entities."""

    def __init__(self, session) -> None:
        super().__init__(CatalogLineage, session)

    async def get_lineage_for_asset(self, asset_id: uuid.UUID) -> Sequence[CatalogLineage]:
        """Fetch outgoing and incoming lineage edges for an asset."""
        stmt = (
            select(CatalogLineage)
            .where(
                (CatalogLineage.source_asset_id == asset_id)
                | (CatalogLineage.target_asset_id == asset_id)
            )
            .options(
                selectinload(CatalogLineage.source_asset),
                selectinload(CatalogLineage.target_asset),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class GlossaryTermRepository(BaseRepository[GlossaryTerm]):
    """Repository for managing GlossaryTerm entities."""

    def __init__(self, session) -> None:
        super().__init__(GlossaryTerm, session)

    async def get_all_terms(self) -> Sequence[GlossaryTerm]:
        """Fetch all business glossary terms ordered by term asc."""
        stmt = select(GlossaryTerm).order_by(GlossaryTerm.term.asc())
        res = await self._session.execute(stmt)
        return res.scalars().all()


class GovernancePolicyRepository(BaseRepository[GovernancePolicy]):
    """Repository for managing GovernancePolicy entities."""

    def __init__(self, session) -> None:
        super().__init__(GovernancePolicy, session)

    async def get_all_policies(self) -> Sequence[GovernancePolicy]:
        """Fetch all governance policies ordered by policy_name asc."""
        stmt = select(GovernancePolicy).order_by(GovernancePolicy.policy_name.asc())
        res = await self._session.execute(stmt)
        return res.scalars().all()
