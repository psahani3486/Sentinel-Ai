"""
Sentinel AI — Catalog Executor

Executes catalog processors and constructs directed acyclic graph (DAG) lineage representations.
"""

import uuid
from typing import Any

from app.catalog.base_processor import CatalogAssetMetadata
from app.catalog.registry import CatalogRegistry, get_catalog_registry


class CatalogExecutor:
    """Executes catalog metadata extraction and constructs lineage DAG graphs."""

    def __init__(self, registry: CatalogRegistry | None = None) -> None:
        self._registry = registry or get_catalog_registry()

    def process_all(self, payload: dict[str, Any]) -> list[CatalogAssetMetadata]:
        """Execute all registered catalog processors."""
        results = []
        for proc in self._registry.get_all():
            meta = proc.process_asset(payload)
            results.append(meta)
        return results

    def build_lineage_dag(self, source_id: uuid.UUID, target_id: uuid.UUID, relationship_type: str = "TRANSFORMS") -> dict[str, Any]:
        """
        Construct directed acyclic graph (DAG) lineage edge object.
        """
        return {
            "source": str(source_id),
            "target": str(target_id),
            "relationship_type": relationship_type,
            "dag_nodes": [
                {"id": str(source_id), "label": "Source Data Asset", "type": "dataset"},
                {"id": str(target_id), "label": "Target Processing Pipeline", "type": "workflow"},
            ],
            "dag_edges": [
                {"source": str(source_id), "target": str(target_id), "label": relationship_type},
            ],
        }
