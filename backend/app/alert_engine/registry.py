"""
Sentinel AI — Alert Rule Registry

Registry Pattern mapping AlertType enums to concrete rule strategy instances.
"""

import logging

from app.alert_engine.base_rule import BaseAlertRule
from app.alert_engine.rules import (
    CriticalValidationRule,
    DataDriftRule,
    DatasetFreshnessRule,
    JobFailureRule,
    PipelineFailureRule,
    PipelineTimeoutRule,
    QualityScoreDropRule,
    RepeatedFailureRule,
    SchemaChangeRule,
    ValidationFailureRule,
)
from app.models.enums import AlertType

logger = logging.getLogger(__name__)


class AlertRegistry:
    """Registry maintaining instances of all automated alert evaluation rules."""

    def __init__(self) -> None:
        self._rules: dict[AlertType, BaseAlertRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default 10 alert rules."""
        rules = [
            QualityScoreDropRule(),
            ValidationFailureRule(),
            CriticalValidationRule(),
            SchemaChangeRule(),
            DataDriftRule(),
            PipelineFailureRule(),
            PipelineTimeoutRule(),
            JobFailureRule(),
            DatasetFreshnessRule(),
            RepeatedFailureRule(),
        ]
        for rule in rules:
            self.register(rule)

    def register(self, rule: BaseAlertRule) -> None:
        """Register an alert rule strategy."""
        self._rules[rule.alert_type] = rule
        logger.debug("Registered Alert Rule Strategy: %s", rule.alert_type.value)

    def get(self, alert_type: AlertType) -> BaseAlertRule:
        """Retrieve rule strategy by AlertType."""
        rule = self._rules.get(alert_type)
        if not rule:
            raise KeyError(f"No alert rule registered for type '{alert_type}'")
        return rule

    def get_all(self) -> list[BaseAlertRule]:
        """Return list of all registered rules."""
        return list(self._rules.values())


# Global default registry singleton
_default_registry: AlertRegistry | None = None


def get_alert_registry() -> AlertRegistry:
    """Return singleton AlertRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = AlertRegistry()
    return _default_registry
