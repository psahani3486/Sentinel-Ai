"""
Sentinel AI — Built-in Catalog Processors

Implements catalog metadata strategy processors:
1. Dataset Catalog Processor
2. Workflow Catalog Processor
3. Governance Policy Processor
"""

from typing import Any

from app.catalog.base_processor import BaseCatalogProcessor, CatalogAssetMetadata
from app.models.enums import AssetType, DataSensitivity


class DatasetCatalogProcessor(BaseCatalogProcessor):
    @property
    def processor_name(self) -> str:
        return "DatasetCatalogProcessor"

    def process_asset(self, payload: dict[str, Any]) -> CatalogAssetMetadata:
        return CatalogAssetMetadata(
            name=payload.get("name", "Industrial Sensor Telemetry Stream"),
            asset_type=AssetType.DATASET,
            domain=payload.get("domain", "Industrial IoT"),
            owner=payload.get("owner", "Data Engineering Team"),
            steward=payload.get("steward", "Data Governance Officer"),
            business_description=payload.get(
                "business_description",
                "Primary operational telemetry stream capturing real-time industrial sensor readings.",
            ),
            technical_description=payload.get(
                "technical_description",
                "PostgreSQL database table with automated quality contract checks.",
            ),
            sensitivity=DataSensitivity.INTERNAL,
            tags=["iot", "telemetry", "production"],
            classifications=["Operational Data", "SLA Critical"],
            dataset_id=payload.get("dataset_id"),
        )


class WorkflowCatalogProcessor(BaseCatalogProcessor):
    @property
    def processor_name(self) -> str:
        return "WorkflowCatalogProcessor"

    def process_asset(self, payload: dict[str, Any]) -> CatalogAssetMetadata:
        return CatalogAssetMetadata(
            name=payload.get("name", "End-to-End Incident Investigation Pipeline"),
            asset_type=AssetType.PIPELINE,
            domain=payload.get("domain", "Observability"),
            owner=payload.get("owner", "Platform Operations"),
            steward=payload.get("steward", "SRE Lead"),
            business_description=payload.get(
                "business_description",
                "Automated DAG pipeline executing cross-module telemetry ingestion and RCA.",
            ),
            technical_description=payload.get(
                "technical_description",
                "Airflow-style 9-step DAG execution pipeline.",
            ),
            sensitivity=DataSensitivity.INTERNAL,
            tags=["pipeline", "workflow", "dag"],
            classifications=["Automated Pipeline"],
        )


class GovernancePolicyProcessor(BaseCatalogProcessor):
    @property
    def processor_name(self) -> str:
        return "GovernancePolicyProcessor"

    def process_asset(self, payload: dict[str, Any]) -> CatalogAssetMetadata:
        return CatalogAssetMetadata(
            name=payload.get("name", "GDPR / PII Data Retention Policy"),
            asset_type=AssetType.TABLE,
            domain=payload.get("domain", "Compliance"),
            owner=payload.get("owner", "Security & Legal"),
            steward=payload.get("steward", "Chief Data Officer"),
            business_description=payload.get(
                "business_description",
                "Compliance policy governing data retention, PII classifications, and audit logs.",
            ),
            technical_description=payload.get(
                "technical_description",
                "Automated 365-day retention policy.",
            ),
            sensitivity=DataSensitivity.RESTRICTED,
            tags=["policy", "compliance", "gdpr"],
            classifications=["Compliance Mandate"],
        )
