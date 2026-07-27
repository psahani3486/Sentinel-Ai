"""Sample Regex Anomaly Rule Plugin implementation."""

from typing import Any
from app.plugins.base_plugin import BasePlugin


class RegexAnomalyRulePlugin(BasePlugin):
    """Developer SDK Example: Custom Regex Anomaly Rule Plugin."""

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        return True

    def execute(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "rule_name": "RegexAnomaly",
            "passed": True,
            "anomalies_detected": 0,
        }

    def shutdown(self) -> None:
        pass
