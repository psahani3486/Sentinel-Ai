"""
Sentinel AI — Catalog Service

Service layer managing data catalog indexing, lineage DAG generation, glossary lookup,
and governance policy queries.
"""

import logging
import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.engine import CatalogEngine
from app.catalog.reporter import CatalogReporter
from app.models.catalog import CatalogAsset, CatalogLineage, GlossaryTerm, GovernancePolicy
from app.models.enums import AssetType, DataSensitivity, LifecycleStatus
from app.repositories.catalog_repository import (
    CatalogAssetRepository,
    CatalogLineageRepository,
    GlossaryTermRepository,
    GovernancePolicyRepository,
)

logger = logging.getLogger(__name__)


class CatalogService:
    """Coordinates catalog metadata indexing, lineage DAG generation, and governance lookup."""

    def __init__(
        self,
        db_session: AsyncSession,
        asset_repo: CatalogAssetRepository | None = None,
        lineage_repo: CatalogLineageRepository | None = None,
        glossary_repo: GlossaryTermRepository | None = None,
        policy_repo: GovernancePolicyRepository | None = None,
        engine: CatalogEngine | None = None,
        reporter: CatalogReporter | None = None,
    ) -> None:
        self._session = db_session
        self._asset_repo = asset_repo or CatalogAssetRepository(db_session)
        self._lineage_repo = lineage_repo or CatalogLineageRepository(db_session)
        self._glossary_repo = glossary_repo or GlossaryTermRepository(db_session)
        self._policy_repo = policy_repo or GovernancePolicyRepository(db_session)
        self._engine = engine or CatalogEngine()
        self._reporter = reporter or CatalogReporter()

    async def seed_initial_catalog(self) -> Sequence[CatalogAsset]:
        """Seed initial catalog assets, lineage edges, glossary terms, and governance policies."""
        assets = await self._asset_repo.get_all_assets()
        if not assets:
            # 1. Assets
            a1 = CatalogAsset(
                name="Industrial Sensor Telemetry Stream",
                asset_type=AssetType.DATASET,
                domain="Industrial IoT",
                owner="Data Engineering Team",
                steward="Data Governance Officer",
                business_description="Primary operational telemetry stream capturing real-time industrial sensor readings.",
                technical_description="PostgreSQL database table with automated quality contract checks.",
                sensitivity=DataSensitivity.INTERNAL,
                retention_period_days=365,
                lifecycle_status=LifecycleStatus.ACTIVE,
                tags={"tags": ["iot", "telemetry", "production"]},
                classifications={"classifications": ["Operational Data", "SLA Critical"]},
            )
            a1 = await self._asset_repo.create(a1)

            a2 = CatalogAsset(
                name="End-to-End Incident Investigation Pipeline",
                asset_type=AssetType.PIPELINE,
                domain="Observability",
                owner="Platform Operations",
                steward="SRE Lead",
                business_description="Automated DAG pipeline executing cross-module telemetry ingestion and RCA.",
                technical_description="Airflow-style 9-step DAG execution pipeline.",
                sensitivity=DataSensitivity.INTERNAL,
                retention_period_days=90,
                lifecycle_status=LifecycleStatus.ACTIVE,
                tags={"tags": ["pipeline", "workflow", "dag"]},
                classifications={"classifications": ["Automated Pipeline"]},
            )
            a2 = await self._asset_repo.create(a2)

            # 2. Lineage Edge: a1 -> a2
            lineage = CatalogLineage(
                source_asset_id=a1.id,
                target_asset_id=a2.id,
                relationship_type="TRANSFORMS",
                lineage_dag={
                    "source": str(a1.id),
                    "target": str(a2.id),
                    "relationship": "TRANSFORMS",
                },
            )
            await self._lineage_repo.create(lineage)

            # 3. Glossary Term
            term = GlossaryTerm(
                term="Data Quality SLA",
                definition="Contractual threshold requiring at least 95% valid sensor observations per ingestion batch.",
                domain="Industrial IoT",
                related_assets={"assets": [str(a1.id)]},
            )
            await self._glossary_repo.create(term)

            # 4. Governance Policy
            policy = GovernancePolicy(
                policy_name="GDPR / PII Data Retention Policy",
                category="Data Governance",
                rules_definition={"max_retention_days": 365, "pii_masking": "required"},
                compliance_status="COMPLIANT",
            )
            await self._policy_repo.create(policy)

            logger.info("Seeded initial Data Catalog ecosystem entities.")

        return await self._asset_repo.get_all_assets()

    async def get_assets(self, skip: int = 0, limit: int = 50) -> Sequence[CatalogAsset]:
        """Fetch paginated catalog assets."""
        assets = await self._asset_repo.get_all_assets(skip=skip, limit=limit)
        if not assets:
            return await self.seed_initial_catalog()
        return assets

    async def get_asset_detail(self, asset_id: uuid.UUID) -> CatalogAsset | None:
        """Fetch detailed catalog asset by ID with lineage."""
        return await self._asset_repo.get_by_id_with_lineage(asset_id)

    async def get_lineage(self, asset_id: uuid.UUID) -> Sequence[CatalogLineage]:
        """Fetch lineage DAG edges connected to an asset."""
        return await self._lineage_repo.get_lineage_for_asset(asset_id)

    async def get_glossary(self) -> Sequence[GlossaryTerm]:
        """Fetch business glossary terms."""
        terms = await self._glossary_repo.get_all_terms()
        if not terms:
            await self.seed_initial_catalog()
            return await self._glossary_repo.get_all_terms()
        return terms

    async def get_policies(self) -> Sequence[GovernancePolicy]:
        """Fetch governance policies."""
        policies = await self._policy_repo.get_all_policies()
        if not policies:
            await self.seed_initial_catalog()
            return await self._policy_repo.get_all_policies()
        return policies
