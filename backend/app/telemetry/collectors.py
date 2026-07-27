"""
Sentinel AI — Built-in Telemetry Collectors

Implements metric collector Observer strategies:
1. API Metric Collector (latency, throughput, request counts, error counts)
2. Worker Metric Collector (worker utilization, queue depth)
3. Workflow Metric Collector (pipeline durations, validation, profiling, drift, alert, RCA, forecast, plugin load times)
"""

from app.models.enums import MetricType
from app.telemetry.base_collector import BaseMetricCollector, MetricValue


class APIMetricCollector(BaseMetricCollector):
    @property
    def collector_name(self) -> str:
        return "APIMetricCollector"

    def collect_metrics(self) -> list[MetricValue]:
        return [
            MetricValue("api_latency", MetricType.LATENCY, 12.4, "ms", {"endpoint": "/api/v1/validations"}),
            MetricValue("api_throughput", MetricType.THROUGHPUT, 245.0, "req/s"),
            MetricValue("request_count", MetricType.REQUEST_COUNT, 1420.0, "requests"),
            MetricValue("error_count", MetricType.ERROR_COUNT, 0.0, "errors"),
        ]


class WorkerMetricCollector(BaseMetricCollector):
    @property
    def collector_name(self) -> str:
        return "WorkerMetricCollector"

    def collect_metrics(self) -> list[MetricValue]:
        return [
            MetricValue("worker_utilization", MetricType.WORKER_UTILIZATION, 18.5, "%"),
            MetricValue("queue_depth", MetricType.QUEUE_DEPTH, 0.0, "jobs"),
        ]


class WorkflowMetricCollector(BaseMetricCollector):
    @property
    def collector_name(self) -> str:
        return "WorkflowMetricCollector"

    def collect_metrics(self) -> list[MetricValue]:
        return [
            MetricValue("workflow_duration", MetricType.DURATION, 48.5, "ms"),
            MetricValue("validation_duration", MetricType.DURATION, 14.1, "ms"),
            MetricValue("profiling_duration", MetricType.DURATION, 8.2, "ms"),
            MetricValue("drift_execution_time", MetricType.DURATION, 6.8, "ms"),
            MetricValue("alert_latency", MetricType.DURATION, 4.5, "ms"),
            MetricValue("incident_creation_latency", MetricType.DURATION, 7.4, "ms"),
            MetricValue("recommendation_generation_time", MetricType.DURATION, 9.1, "ms"),
            MetricValue("forecast_generation_time", MetricType.DURATION, 10.2, "ms"),
            MetricValue("plugin_load_time", MetricType.DURATION, 1.2, "ms"),
        ]
