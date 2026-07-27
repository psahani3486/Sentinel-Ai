"""
Sentinel AI — Forecast Reporter

Formats forecast telemetry reports for dashboard display.
"""

from typing import Any


class ForecastReporter:
    """Formats forecast executions for UI dashboard rendering."""

    def build_dashboard_summary(self, forecast_runs: list[Any]) -> dict[str, Any]:
        """Build risk level telemetry summary."""
        high_risk_count = 0
        total = len(forecast_runs)

        for run in forecast_runs:
            risk = str(getattr(run, "overall_risk_level", "low")).lower()
            if risk in ("critical", "high"):
                high_risk_count += 1

        return {
            "total_forecasts": total,
            "high_risk_count": high_risk_count,
            "latest_run": forecast_runs[0] if forecast_runs else None,
        }
