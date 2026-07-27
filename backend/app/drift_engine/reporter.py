"""
Sentinel AI — Drift Reporter

Generates diagnostic summaries and telemetry reports from DriftEngine results.
"""

from typing import Any

from app.drift_engine.base_detector import DriftResultItem
from app.models.enums import DriftSeverity, DriftStatus


class DriftReporter:
    """Formats drift telemetry into structured diagnostic reports."""

    def build_summary(
        self,
        status: DriftStatus,
        overall_score: float,
        drifted_columns_count: int,
        total_columns_analyzed: int,
        results: list[DriftResultItem],
    ) -> dict[str, Any]:
        """Build JSON summary report."""
        severity_counts = {
            DriftSeverity.CRITICAL.value: 0,
            DriftSeverity.HIGH.value: 0,
            DriftSeverity.MEDIUM.value: 0,
            DriftSeverity.LOW.value: 0,
            DriftSeverity.INFO.value: 0,
        }

        detector_counts: dict[str, int] = {}
        for r in results:
            if r.drift_detected:
                sev_key = r.severity.value if hasattr(r.severity, "value") else str(r.severity)
                severity_counts[sev_key] = severity_counts.get(sev_key, 0) + 1

                det_key = r.detector_type.value if hasattr(r.detector_type, "value") else str(r.detector_type)
                detector_counts[det_key] = detector_counts.get(det_key, 0) + 1

        return {
            "dataset_drift_status": status.value if hasattr(status, "value") else str(status),
            "overall_drift_score": overall_score,
            "drifted_columns_count": drifted_columns_count,
            "total_columns_analyzed": total_columns_analyzed,
            "severity_breakdown": severity_counts,
            "detector_breakdown": detector_counts,
        }
