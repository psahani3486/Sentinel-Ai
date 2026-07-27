"""
Sentinel AI — Analysis Reporter

Formats diagnostic RCA reports and confidence score telemetry for frontend rendering.
"""

from typing import Any


class AnalysisReporter:
    """Formats root cause analysis reports for dashboard display."""

    def build_dashboard_summary(self, analyses: list[Any]) -> dict[str, Any]:
        """Build high-level RCA engine telemetry metrics."""
        total = len(analyses)
        avg_confidence = sum([getattr(a, "confidence_score", 0.0) for a in analyses]) / total if total > 0 else 0.0

        return {
            "total_analyses": total,
            "average_confidence_score": round(avg_confidence, 1),
            "latest_run": analyses[0] if analyses else None,
        }
