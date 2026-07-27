"""
Sentinel AI — Recommendation Reporter

Formats ranked recommendation telemetry for dashboard and Priority Matrix display.
"""

from typing import Any


class RecommendationReporter:
    """Formats recommendations for UI dashboard rendering."""

    def build_dashboard_summary(self, recommendations: list[Any]) -> dict[str, Any]:
        """Build priority matrix telemetry summary."""
        high_impact_low_effort = 0
        total = len(recommendations)

        for rec in recommendations:
            imp = getattr(rec, "estimated_impact", "HIGH").upper()
            eff = getattr(rec, "estimated_effort", "LOW").upper()
            if imp == "HIGH" and eff == "LOW":
                high_impact_low_effort += 1

        return {
            "total_recommendations": total,
            "quick_wins_count": high_impact_low_effort,
            "highest_priority_item": recommendations[0] if recommendations else None,
        }
