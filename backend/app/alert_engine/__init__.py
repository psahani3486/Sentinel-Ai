"""Alert Engine Package."""

from app.alert_engine.base_rule import AlertCandidate, BaseAlertRule
from app.alert_engine.engine import AlertEngine, escalate_severity
from app.alert_engine.executor import AlertExecutor
from app.alert_engine.registry import AlertRegistry, get_alert_registry
from app.alert_engine.reporter import AlertReporter

__all__ = [
    "BaseAlertRule",
    "AlertCandidate",
    "AlertRegistry",
    "get_alert_registry",
    "AlertExecutor",
    "AlertEngine",
    "escalate_severity",
    "AlertReporter",
]
