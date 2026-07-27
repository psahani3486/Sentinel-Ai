"""
Sentinel AI — Catalog Strategy Registry

Registry Pattern maintaining instances of metadata processors.
"""

import logging

from app.catalog.base_processor import BaseCatalogProcessor
from app.catalog.processors import (
    DatasetCatalogProcessor,
    GovernancePolicyProcessor,
    WorkflowCatalogProcessor,
)

logger = logging.getLogger(__name__)


class CatalogRegistry:
    """Registry maintaining catalog processor strategies."""

    def __init__(self) -> None:
        self._processors: dict[str, BaseCatalogProcessor] = {}
        self._register_default_processors()

    def _register_default_processors(self) -> None:
        """Register default catalog processors."""
        processors = [
            DatasetCatalogProcessor(),
            WorkflowCatalogProcessor(),
            GovernancePolicyProcessor(),
        ]
        for p in processors:
            self.register(p)

    def register(self, processor: BaseCatalogProcessor) -> None:
        """Register a catalog processor strategy."""
        self._processors[processor.processor_name] = processor
        logger.debug("Registered Catalog Processor: %s", processor.processor_name)

    def get(self, name: str) -> BaseCatalogProcessor:
        """Retrieve catalog processor by name."""
        return self._processors.get(name, DatasetCatalogProcessor())

    def get_all(self) -> list[BaseCatalogProcessor]:
        """Return list of all registered processors."""
        return list(self._processors.values())


# Global default registry singleton
_default_registry: CatalogRegistry | None = None


def get_catalog_registry() -> CatalogRegistry:
    """Return singleton CatalogRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = CatalogRegistry()
    return _default_registry
