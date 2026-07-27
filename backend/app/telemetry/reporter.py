"""
Sentinel AI — Telemetry Reporter

Formats metric dashboards, subsystem health matrices, and trace waterfall timelines for UI rendering.
"""

from typing import Any


class TelemetryReporter:
    """Formats platform telemetry metrics and health status for UI display."""

    def build_dashboard_summary(self, metrics: list[Any], health: dict[str, Any]) -> dict[str, Any]:
        """Build telemetry ecosystem summary."""
        healthy_cnt = sum(
            1 for status in health.values()
            if str(getattr(status, "value", status)).lower() == "healthy"
        )
        total_subsystems = len(health)

        return {
            "total_metrics_samples": len(metrics),
            "total_subsystems": total_subsystems,
            "healthy_subsystems_count": healthy_cnt,
            "system_health_percent": (healthy_cnt / total_subsystems * 100.0) if total_subsystems > 0 else 100.0,
        }
