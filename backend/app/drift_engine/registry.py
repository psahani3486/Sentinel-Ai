"""
Sentinel AI — Drift Detector Registry

Registry Pattern mapping DetectorType enums to concrete detector strategy instances.
"""

import logging

from app.drift_engine.base_detector import BaseDriftDetector
from app.drift_engine.detectors import (
    CardinalityDriftDetector,
    CategoryDistributionDetector,
    JensenShannonDetector,
    KLDivergenceDetector,
    MeanDriftDetector,
    MissingValueDriftDetector,
    NumericDistributionDetector,
    PSIDetector,
    StdDriftDetector,
    WassersteinDetector,
)
from app.models.enums import DetectorType

logger = logging.getLogger(__name__)


class DriftRegistry:
    """Registry maintaining instances of all statistical drift detectors."""

    def __init__(self) -> None:
        self._detectors: dict[DetectorType, BaseDriftDetector] = {}
        self._register_default_detectors()

    def _register_default_detectors(self) -> None:
        """Register default 10 drift detectors."""
        detectors = [
            PSIDetector(),
            JensenShannonDetector(),
            KLDivergenceDetector(),
            WassersteinDetector(),
            MeanDriftDetector(),
            StdDriftDetector(),
            MissingValueDriftDetector(),
            CardinalityDriftDetector(),
            CategoryDistributionDetector(),
            NumericDistributionDetector(),
        ]
        for det in detectors:
            self.register(det)

    def register(self, detector: BaseDriftDetector) -> None:
        """Register a drift detector instance."""
        self._detectors[detector.detector_type] = detector
        logger.debug("Registered Drift Detector: %s", detector.detector_type.value)

    def get(self, detector_type: DetectorType) -> BaseDriftDetector:
        """Retrieve detector instance by DetectorType."""
        detector = self._detectors.get(detector_type)
        if not detector:
            raise KeyError(f"No drift detector registered for type '{detector_type}'")
        return detector

    def get_all(self) -> list[BaseDriftDetector]:
        """Return list of all registered detectors."""
        return list(self._detectors.values())


# Global default registry instance
_default_registry: DriftRegistry | None = None


def get_drift_registry() -> DriftRegistry:
    """Return singleton DriftRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = DriftRegistry()
    return _default_registry
