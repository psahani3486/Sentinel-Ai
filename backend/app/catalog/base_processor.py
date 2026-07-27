"""
Sentinel AI — Base Catalog Processor & Metadata Interfaces

Defines BaseCatalogProcessor abstract strategy interface, CatalogAssetMetadata,
and LineageEdge dataclasses.
"""

import abc
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import AssetType, DataSensitivity, LifecycleStatus


@dataclass
class LineageEdge:
    """Dataclass defining a directed lineage edge inside a lineage DAG."""

    source_asset_id: uuid.UUID
    target_asset_id: uuid.UUID
    relationship_type: str = "TRANSFORMS"


@dataclass
class CatalogAssetMetadata:
    """Dataclass holding catalog asset metadata."""

    name: str
    asset_type: AssetType
    domain: str = "General"
    owner: str = "Data Engineering"
    steward: str = "Governance Lead"
    business_description: str = "Core dataset asset"
    technical_description: str = "SQL database table asset"
    sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    retention_period_days: int = 365
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    tags: list[str] = field(default_factory=list)
    classifications: list[str] = field(default_factory=list)
    dataset_id: uuid.UUID | None = None


class BaseCatalogProcessor(abc.ABC):
    """Abstract strategy interface for catalog metadata processing."""

    @property
    @abc.abstractmethod
    def processor_name(self) -> str:
        """Return unique catalog processor name."""
        pass

    @abc.abstractmethod
    def process_asset(self, payload: dict[str, Any]) -> CatalogAssetMetadata:
        """Extract and normalize catalog asset metadata."""
        pass
