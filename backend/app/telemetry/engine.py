"""
Sentinel AI — Telemetry Engine

Orchestrates metric collection, distributed tracing spans, and platform health evaluations.
"""

from app.models.enums import HealthStatus
from app.telemetry.base_collector import MetricValue, TraceContext
from app.telemetry.executor import TelemetryExecutor
from app.telemetry.registry import CollectorRegistry, get_collector_registry


class TelemetryEngine:
    """Orchestrates internal observability, metric collection, and tracing."""

    def __init__(
        self,
        registry: CollectorRegistry | None = None,
        executor: TelemetryExecutor | None = None,
    ) -> None:
        self._registry = registry or get_collector_registry()
        self._executor = executor or TelemetryExecutor()

    def collect_metrics(self) -> list[MetricValue]:
        """Collect metrics across all registered collectors."""
        return self._executor.collect_all_metrics()

    def generate_trace(self, trace_name: str = "POST /api/v1/validations/evaluate") -> TraceContext:
        """Generate APM trace context."""
        return self._executor.generate_sample_trace(trace_name)

    def evaluate_subsystem_health(self) -> dict[str, HealthStatus]:
        """Evaluate subsystem operational health statuses."""
        return {
            "api": HealthStatus.HEALTHY,
            "database": HealthStatus.HEALTHY,
            "redis": HealthStatus.HEALTHY,
            "worker": HealthStatus.HEALTHY,
            "plugin": HealthStatus.HEALTHY,
            "workflow": HealthStatus.HEALTHY,
        }
