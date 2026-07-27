"""
Sentinel AI — Alert Executor

Evaluates all registered alert rules against incoming platform event payloads.
"""

from typing import Any

from app.alert_engine.base_rule import AlertCandidate
from app.alert_engine.registry import AlertRegistry, get_alert_registry


class AlertExecutor:
    """Executes registered alert rules against event telemetry payloads."""

    def __init__(self, registry: AlertRegistry | None = None) -> None:
        self._registry = registry or get_alert_registry()

    def evaluate_event(self, event_payload: dict[str, Any]) -> list[AlertCandidate]:
        """
        Evaluate event payload against all registered rules.

        Returns:
            List of generated AlertCandidate items.
        """
        candidates: list[AlertCandidate] = []
        for rule in self._registry.get_all():
            candidate = rule.evaluate(event_payload)
            if candidate is not None:
                candidates.append(candidate)
        return candidates
