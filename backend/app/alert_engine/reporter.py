"""
Sentinel AI — Alert Reporter

Formats diagnostic incident summaries and notification drawer telemetry payload.
"""

from typing import Any

from app.models.enums import AlertSeverity, AlertStatus


class AlertReporter:
    """Formats incident alerts for notification drawers and diagnostic timelines."""

    def build_drawer_summary(self, alerts: list[Any]) -> dict[str, Any]:
        """Build structured notification drawer payload."""
        counts_by_severity = {
            AlertSeverity.CRITICAL.value: 0,
            AlertSeverity.HIGH.value: 0,
            AlertSeverity.MEDIUM.value: 0,
            AlertSeverity.LOW.value: 0,
            AlertSeverity.INFO.value: 0,
        }

        counts_by_status = {
            AlertStatus.OPEN.value: 0,
            AlertStatus.ACKNOWLEDGED.value: 0,
            AlertStatus.RESOLVED.value: 0,
            AlertStatus.SUPPRESSED.value: 0,
        }

        for alt in alerts:
            sev_key = alt.severity.value if hasattr(alt.severity, "value") else str(alt.severity)
            stat_key = alt.status.value if hasattr(alt.status, "value") else str(alt.status)

            counts_by_severity[sev_key] = counts_by_severity.get(sev_key, 0) + 1
            counts_by_status[stat_key] = counts_by_status.get(stat_key, 0) + 1

        return {
            "total_alerts": len(alerts),
            "unresolved_count": counts_by_status.get(AlertStatus.OPEN.value, 0) + counts_by_status.get(AlertStatus.ACKNOWLEDGED.value, 0),
            "severity_breakdown": counts_by_severity,
            "status_breakdown": counts_by_status,
        }
