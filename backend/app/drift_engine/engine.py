"""
Sentinel AI — Data Drift Engine

Main coordinator for feature distribution comparison, overall drift scoring,
and dataset drift status assignment.
"""

import time
from typing import Any

from app.drift_engine.base_detector import DriftResultItem
from app.drift_engine.executor import DriftExecutor
from app.models.enums import DriftStatus


class DriftEngine:
    """Coordinates drift analysis across all dataset columns and computes dataset-level metrics."""

    def __init__(self, executor: DriftExecutor | None = None) -> None:
        self._executor = executor or DriftExecutor()

    def run_drift_analysis(
        self,
        baseline_dataset: dict[str, list[Any]],
        current_dataset: dict[str, list[Any]],
        column_types: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Compare current dataset against baseline dataset across all shared columns.

        Returns:
            Dict containing overall score, status, execution duration, and per-column DriftResultItems.
        """
        start_time = time.time()
        col_types = column_types or {}

        shared_cols = sorted(list(set(baseline_dataset.keys()).intersection(set(current_dataset.keys()))))
        all_results: list[DriftResultItem] = []
        drifted_columns: set[str] = set()

        for col in shared_cols:
            base_vals = baseline_dataset[col]
            curr_vals = current_dataset[col]
            c_type = col_types.get(col)

            items = self._executor.execute_column_detectors(
                baseline_values=base_vals,
                current_values=curr_vals,
                column_name=col,
                column_type=c_type,
            )
            all_results.extend(items)

            if any(it.drift_detected for it in items):
                drifted_columns.add(col)

        # Compute overall drift score (0 - 100)
        total_cols = max(len(shared_cols), 1)
        drift_ratio = len(drifted_columns) / total_cols
        overall_score = round(drift_ratio * 100.0, 1)

        # Determine overall DriftStatus
        if overall_score >= 50.0:
            status = DriftStatus.CRITICAL
        elif overall_score >= 30.0:
            status = DriftStatus.HIGH
        elif overall_score >= 15.0:
            status = DriftStatus.MEDIUM
        elif overall_score > 0.0:
            status = DriftStatus.LOW
        else:
            status = DriftStatus.NO_DRIFT

        exec_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": status,
            "overall_drift_score": overall_score,
            "drifted_columns_count": len(drifted_columns),
            "total_columns_analyzed": len(shared_cols),
            "execution_time_ms": exec_ms,
            "results": all_results,
        }
