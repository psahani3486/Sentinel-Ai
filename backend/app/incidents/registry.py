"""
Sentinel AI — Incident Correlator Registry

Registry Pattern maintaining instances of all telemetry signal correlators.
"""

import logging

from app.incidents.base_correlator import BaseIncidentCorrelator
from app.incidents.correlators import (
    AIAnalysisIncidentCorrelator,
    AlertIncidentCorrelator,
    DriftIncidentCorrelator,
    SchemaIncidentCorrelator,
    ValidationIncidentCorrelator,
)

logger = logging.getLogger(__name__)


class IncidentRegistry:
    """Registry maintaining instances of all telemetry signal correlators."""

    def __init__(self) -> None:
        self._correlators: list[BaseIncidentCorrelator] = []
        self._register_default_correlators()

    def _register_default_correlators(self) -> None:
        """Register default signal correlators."""
        correlators = [
            ValidationIncidentCorrelator(),
            DriftIncidentCorrelator(),
            SchemaIncidentCorrelator(),
            AlertIncidentCorrelator(),
            AIAnalysisIncidentCorrelator(),
        ]
        for c in correlators:
            self.register(c)

    def register(self, correlator: BaseIncidentCorrelator) -> None:
        """Register an incident correlator."""
        self._correlators.append(correlator)
        logger.debug("Registered Incident Correlator: %s", correlator.name)

    def get_all(self) -> list[BaseIncidentCorrelator]:
        """Return list of all registered correlators."""
        return list(self._correlators)


# Global default registry singleton
_default_registry: IncidentRegistry | None = None


def get_incident_registry() -> IncidentRegistry:
    """Return singleton IncidentRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = IncidentRegistry()
    return _default_registry
