"""
Sentinel AI — Telemetry Collector Registry

Observer Registry Pattern maintaining instances of metric collectors.
"""

import logging

from app.telemetry.base_collector import BaseMetricCollector
from app.telemetry.collectors import (
    APIMetricCollector,
    WorkerMetricCollector,
    WorkflowMetricCollector,
)

logger = logging.getLogger(__name__)


class CollectorRegistry:
    """Observer registry maintaining metric collector strategies."""

    def __init__(self) -> None:
        self._collectors: dict[str, BaseMetricCollector] = {}
        self._register_default_collectors()

    def _register_default_collectors(self) -> None:
        """Register default metric collectors."""
        collectors = [
            APIMetricCollector(),
            WorkerMetricCollector(),
            WorkflowMetricCollector(),
        ]
        for c in collectors:
            self.register(c)

    def register(self, collector: BaseMetricCollector) -> None:
        """Register a metric collector strategy."""
        self._collectors[collector.collector_name] = collector
        logger.debug("Registered Metric Collector: %s", collector.collector_name)

    def get_all(self) -> list[BaseMetricCollector]:
        """Return list of all registered collectors."""
        return list(self._collectors.values())


# Global default registry singleton
_default_registry: CollectorRegistry | None = None


def get_collector_registry() -> CollectorRegistry:
    """Return singleton CollectorRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = CollectorRegistry()
    return _default_registry
