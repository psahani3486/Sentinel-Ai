"""
Sentinel AI — Base Drift Detector

Defines the BaseDriftDetector abstract strategy interface and DriftResultItem dataclass.
"""

import abc
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import DetectorType, DriftSeverity


@dataclass
class DriftResultItem:
    """Standardized output structure from a drift detector evaluation."""

    column_name: str
    column_type: str
    detector_type: DetectorType
    drift_detected: bool
    drift_score: float
    threshold: float
    severity: DriftSeverity
    explanation: str
    metrics_data: dict[str, Any] = field(default_factory=dict)


class BaseDriftDetector(abc.ABC):
    """Abstract strategy base class for statistical data drift detectors."""

    @property
    @abc.abstractmethod
    def detector_type(self) -> DetectorType:
        """Return the unique DetectorType enum key."""
        pass

    @property
    @abc.abstractmethod
    def default_threshold(self) -> float:
        """Default mathematical threshold value for drift detection."""
        pass

    @abc.abstractmethod
    def detect(
        self,
        baseline_data: list[Any],
        current_data: list[Any],
        column_name: str,
        column_type: str = "numeric",
        threshold: float | None = None,
    ) -> DriftResultItem:
        """
        Evaluate drift between baseline reference distribution and current distribution.

        Args:
            baseline_data: List of feature values from baseline dataset version.
            current_data: List of feature values from current dataset version.
            column_name: Target column identifier.
            column_type: Feature data type ('numeric', 'categorical', 'boolean', 'datetime').
            threshold: Custom drift threshold override.

        Returns:
            DriftResultItem containing score, detection status, severity, and diagnostic breakdown.
        """
        pass
