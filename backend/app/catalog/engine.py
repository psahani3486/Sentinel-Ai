"""
Sentinel AI — Catalog Engine

Orchestrates catalog metadata indexing, lineage DAG generation, and governance checks.
"""

from typing import Any

from app.catalog.base_processor import CatalogAssetMetadata
from app.catalog.executor import CatalogExecutor
from app.catalog.registry import CatalogRegistry, get_catalog_registry


class CatalogEngine:
    """Orchestrates enterprise metadata indexing and lineage DAG generation."""

    def __init__(
        self,
        registry: CatalogRegistry | None = None,
        executor: CatalogExecutor | None = None,
    ) -> None:
        self._registry = registry or get_catalog_registry()
        self._executor = executor or CatalogExecutor()

    def index_assets(self, payload: dict[str, Any] | None = None) -> list[CatalogAssetMetadata]:
        """Index catalog assets across all registered processors."""
        return self._executor.process_all(payload or {})
