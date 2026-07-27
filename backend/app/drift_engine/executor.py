"""
Sentinel AI — Drift Executor

Executes compatible drift detectors on column data based on automatic data type detection.
"""

import math
from typing import Any

from app.drift_engine.base_detector import DriftResultItem
from app.drift_engine.registry import DriftRegistry, get_drift_registry
from app.models.enums import DetectorType


def infer_column_type(data: list[Any]) -> str:
    """
    Infer column data type ('numeric', 'categorical', 'boolean', 'datetime').
    """
    non_nulls = [x for x in data if x is not None]
    if not non_nulls:
        return "numeric"

    num_count = 0
    bool_count = 0
    date_count = 0

    for x in non_nulls:
        if isinstance(x, bool):
            bool_count += 1
            continue
        try:
            val = float(x)
            if not (math.isnan(val) or math.isinf(val)):
                num_count += 1
                continue
        except (ValueError, TypeError):
            pass

        s = str(x).lower().strip()
        if s in ("true", "false", "t", "f", "1", "0"):
            bool_count += 1
        elif any(char in s for char in ("-", "/", ":")) and len(s) >= 8:
            date_count += 1

    total = len(non_nulls)
    if num_count / total >= 0.7:
        return "numeric"
    if bool_count / total >= 0.7:
        return "boolean"
    if date_count / total >= 0.5:
        return "datetime"
    return "categorical"


class DriftExecutor:
    """Executes target detectors against column dataset feature vectors."""

    def __init__(self, registry: DriftRegistry | None = None) -> None:
        self._registry = registry or get_drift_registry()

    def get_compatible_detector_types(self, column_type: str) -> list[DetectorType]:
        """Return compatible DetectorType list based on column classification."""
        if column_type == "numeric":
            return [
                DetectorType.PSI,
                DetectorType.JENSEN_SHANNON,
                DetectorType.KL_DIVERGENCE,
                DetectorType.WASSERSTEIN,
                DetectorType.MEAN_DRIFT,
                DetectorType.STD_DRIFT,
                DetectorType.MISSING_VALUE_DRIFT,
                DetectorType.NUMERIC_DISTRIBUTION_DRIFT,
            ]
        elif column_type in ("categorical", "boolean"):
            return [
                DetectorType.MISSING_VALUE_DRIFT,
                DetectorType.CARDINALITY_DRIFT,
                DetectorType.CATEGORY_DISTRIBUTION_DRIFT,
            ]
        else:  # datetime or unknown
            return [
                DetectorType.MISSING_VALUE_DRIFT,
                DetectorType.CARDINALITY_DRIFT,
            ]

    def execute_column_detectors(
        self,
        baseline_values: list[Any],
        current_values: list[Any],
        column_name: str,
        column_type: str | None = None,
        thresholds: dict[DetectorType, float] | None = None,
    ) -> list[DriftResultItem]:
        """Execute compatible detectors for a single column."""
        inferred_type = column_type or infer_column_type(baseline_values + current_values)
        detector_types = self.get_compatible_detector_types(inferred_type)
        threshold_map = thresholds or {}

        results: list[DriftResultItem] = []
        for det_type in detector_types:
            detector = self._registry.get(det_type)
            thresh = threshold_map.get(det_type)
            item = detector.detect(
                baseline_data=baseline_values,
                current_data=current_values,
                column_name=column_name,
                column_type=inferred_type,
                threshold=thresh,
            )
            results.append(item)

        return results
