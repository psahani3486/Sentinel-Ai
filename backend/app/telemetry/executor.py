"""
Sentinel AI — Telemetry Executor

Executes metric collectors and generates APM trace contexts with parent-child span waterfall hierarchy.
"""

import datetime
import uuid
from app.models.enums import SpanStatus
from app.telemetry.base_collector import MetricValue, SpanData, TraceContext
from app.telemetry.registry import CollectorRegistry, get_collector_registry


class TelemetryExecutor:
    """Executes metric collection and creates APM trace contexts."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self._registry = registry or get_collector_registry()

    def collect_all_metrics(self) -> list[MetricValue]:
        """Collect metrics from all registered collectors."""
        metrics = []
        for c in self._registry.get_all():
            metrics.extend(c.collect_metrics())
        return metrics

    def generate_sample_trace(self, trace_name: str = "POST /api/v1/validations/evaluate") -> TraceContext:
        """
        Generate an APM TraceContext with parent-child span waterfall hierarchy.
        """
        trace_id_str = f"tr-{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc)

        # Parent Span
        parent_span_id = f"sp-{uuid.uuid4().hex[:8]}"
        parent_span = SpanData(
            span_id=parent_span_id,
            trace_id_str=trace_id_str,
            parent_span_id=None,
            name=trace_name,
            service_name="sentinel-api",
            status=SpanStatus.OK,
            duration_ms=42.5,
            attributes={"http.method": "POST", "http.status_code": 200},
            start_time=now,
            end_time=now + datetime.timedelta(milliseconds=42.5),
        )

        # Child Span 1: DB Query
        child1_id = f"sp-{uuid.uuid4().hex[:8]}"
        child1_span = SpanData(
            span_id=child1_id,
            trace_id_str=trace_id_str,
            parent_span_id=parent_span_id,
            name="SQL Query: FETCH dataset_rules",
            service_name="postgresql",
            status=SpanStatus.OK,
            duration_ms=12.1,
            attributes={"db.system": "postgresql", "db.statement": "SELECT * FROM validation_rules WHERE dataset_id = $1"},
            start_time=now + datetime.timedelta(milliseconds=2.0),
            end_time=now + datetime.timedelta(milliseconds=14.1),
        )

        # Child Span 2: Validation Engine Rule Execution
        child2_id = f"sp-{uuid.uuid4().hex[:8]}"
        child2_span = SpanData(
            span_id=child2_id,
            trace_id_str=trace_id_str,
            parent_span_id=parent_span_id,
            name="Validation Engine: Evaluate Rule Suite",
            service_name="validation-engine",
            status=SpanStatus.OK,
            duration_ms=22.4,
            attributes={"rules_evaluated": 21, "failed_rules": 1},
            start_time=now + datetime.timedelta(milliseconds=15.0),
            end_time=now + datetime.timedelta(milliseconds=37.4),
        )

        return TraceContext(
            trace_id=trace_id_str,
            name=trace_name,
            service_name="sentinel-api",
            duration_ms=42.5,
            status=SpanStatus.OK,
            spans=[parent_span, child1_span, child2_span],
        )
