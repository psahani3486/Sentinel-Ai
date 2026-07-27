"""
Sentinel AI — Alert Engine

Coordinates alert evaluation, fingerprint deduplication, and escalation policies.
"""

from typing import Any

from app.alert_engine.base_rule import AlertCandidate
from app.alert_engine.executor import AlertExecutor
from app.models.enums import AlertSeverity


def escalate_severity(current_severity: AlertSeverity, occurrence_count: int) -> AlertSeverity:
    """
    Escalation policy: Upgrades alert severity based on repeated occurrence count threshold.
    - occurrence >= 5 -> CRITICAL
    - occurrence >= 3 -> HIGH (if currently MEDIUM or LOW)
    """
    if occurrence_count >= 5:
        return AlertSeverity.CRITICAL

    if occurrence_count >= 3:
        if current_severity in (AlertSeverity.INFO, AlertSeverity.LOW, AlertSeverity.MEDIUM):
            return AlertSeverity.HIGH

    return current_severity


class AlertEngine:
    """Coordinates alert evaluation candidates, deduplication rules, and severity escalation policies."""

    def __init__(self, executor: AlertExecutor | None = None) -> None:
        self._executor = executor or AlertExecutor()

    def process_event_payload(self, event_payload: dict[str, Any]) -> list[AlertCandidate]:
        """Evaluate event payload and return candidate alerts."""
        return self._executor.evaluate_event(event_payload)

    def calculate_escalated_severity(
        self, candidate_severity: AlertSeverity, new_occurrence_count: int
    ) -> AlertSeverity:
        """Apply escalation logic to determine final severity."""
        return escalate_severity(candidate_severity, new_occurrence_count)
