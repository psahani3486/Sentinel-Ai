"""
Sentinel AI — Incident Reporter

Formats correlation graph telemetry and incident workspace summaries for UI display.
"""

from typing import Any


class IncidentReporter:
    """Formats incident workspaces for UI dashboard and correlation graph rendering."""

    def build_dashboard_summary(self, incidents: list[Any]) -> dict[str, Any]:
        """Build incident telemetry summary."""
        open_count = 0
        critical_count = 0
        total = len(incidents)

        for inc in incidents:
            st = str(getattr(inc, "status", "open")).lower()
            sev = str(getattr(inc, "severity", "high")).lower()

            if st in ("open", "investigating"):
                open_count += 1
            if sev == "critical":
                critical_count += 1

        return {
            "total_incidents": total,
            "open_incidents_count": open_count,
            "critical_incidents_count": critical_count,
            "latest_incident": incidents[0] if incidents else None,
        }
