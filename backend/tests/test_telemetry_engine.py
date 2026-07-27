"""
Sentinel AI — Phase 7A Platform Telemetry, Metrics & Distributed Tracing Test Suite

Tests Metric Collectors, APM Trace Context & Span Waterfalls, TelemetryEngine,
TelemetryService, and REST API endpoints.
"""

import pytest

from app.telemetry.collectors import (
    APIMetricCollector,
    WorkerMetricCollector,
    WorkflowMetricCollector,
)
from app.telemetry.engine import TelemetryEngine
from app.telemetry.executor import TelemetryExecutor
from app.telemetry.reporter import TelemetryReporter
from app.services.telemetry_service import TelemetryService


# ── Metric Collectors & APM Tracing Tests ──────────────────────────────────────
def test_metric_collectors_and_trace_executor():
    """Test metric collectors and APM trace context waterfall generation."""
    api_c = APIMetricCollector()
    api_m = api_c.collect_metrics()
    assert len(api_m) == 4

    worker_c = WorkerMetricCollector()
    worker_m = worker_c.collect_metrics()
    assert len(worker_m) == 2

    wf_c = WorkflowMetricCollector()
    wf_m = wf_c.collect_metrics()
    assert len(wf_m) == 9

    executor = TelemetryExecutor()
    all_metrics = executor.collect_all_metrics()
    assert len(all_metrics) == 15

    tctx = executor.generate_sample_trace("GET /api/v1/health")
    assert tctx.name == "GET /api/v1/health"
    assert len(tctx.spans) == 3


def test_telemetry_engine_and_reporter():
    """Test TelemetryEngine and TelemetryReporter."""
    engine = TelemetryEngine()
    metrics = engine.collect_metrics()
    health = engine.evaluate_subsystem_health()
    assert len(metrics) == 15
    assert len(health) == 6

    reporter = TelemetryReporter()
    summary = reporter.build_dashboard_summary(metrics, health)
    assert summary["system_health_percent"] == 100.0


@pytest.mark.asyncio
async def test_telemetry_service_and_rest_api(client, auth_headers, db_session):
    """Test TelemetryService and REST API endpoints /telemetry/metrics, /health, /traces, and /traces/{id}."""
    svc = TelemetryService(db_session)
    metrics = await svc.seed_initial_telemetry()
    await db_session.commit()
    assert len(metrics) >= 15

    traces = await svc.get_traces()
    assert len(traces) >= 1
    trace_id_str = traces[0].trace_id

    # 1. Get Metrics via GET
    resp_m = await client.get("/api/v1/telemetry/metrics", headers=auth_headers)
    assert resp_m.status_code == 200
    assert len(resp_m.json()) >= 15

    # 2. Get Health via GET
    resp_h = await client.get("/api/v1/telemetry/health", headers=auth_headers)
    assert resp_h.status_code == 200
    assert resp_h.json()["status"] == "healthy"

    # 3. Get Traces via GET
    resp_t = await client.get("/api/v1/telemetry/traces", headers=auth_headers)
    assert resp_t.status_code == 200
    assert len(resp_t.json()) >= 1

    # 4. Get Trace Detail via GET
    resp_td = await client.get(f"/api/v1/telemetry/traces/{trace_id_str}", headers=auth_headers)
    assert resp_td.status_code == 200
    assert resp_td.json()["trace_id"] == trace_id_str
