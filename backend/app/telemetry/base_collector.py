"""
Sentinel AI — Base Telemetry & APM Tracing Interfaces

Defines BaseMetricCollector Observer strategy interface, MetricValue, SpanData,
and TraceContext dataclasses.
"""

import abc
import datetime
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import MetricType, SpanStatus


@dataclass
class MetricValue:
    """Dataclass holding metric sample data."""

    metric_name: str
    metric_type: MetricType
    value: float
    unit: str = "ms"
    labels: dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanData:
    """Dataclass holding APM trace span waterfall data."""

    span_id: str
    trace_id_str: str
    parent_span_id: str | None
    name: str
    service_name: str = "sentinel-api"
    status: SpanStatus = SpanStatus.OK
    duration_ms: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    start_time: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    end_time: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


@dataclass
class TraceContext:
    """Dataclass holding APM trace context."""

    trace_id: str
    name: str
    service_name: str = "sentinel-api"
    duration_ms: float = 0.0
    status: SpanStatus = SpanStatus.OK
    spans: list[SpanData] = field(default_factory=list)


class BaseMetricCollector(abc.ABC):
    """Abstract Observer strategy interface implemented by all metric collectors."""

    @property
    @abc.abstractmethod
    def collector_name(self) -> str:
        """Return unique collector name."""
        pass

    @abc.abstractmethod
    def collect_metrics(self) -> list[MetricValue]:
        """Collect and return metric samples."""
        pass
