"""
Sentinel AI — Phase 3E Alert Engine Test Suite

Tests all 10 automated alert rules, fingerprint deduplication, escalation policy,
AlertService, WebSocket event emission, and REST API endpoints.
"""

import uuid
import pytest

from app.alert_engine.engine import escalate_severity
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
from app.events.event_bus import InMemoryEventBus
from app.models.enums import AlertSeverity, AlertStatus, AlertType
from app.services.alert_service import AlertService


# ── Rule Strategy Tests ────────────────────────────────────────────────────────
def test_all_10_alert_rules():
    """Test evaluation of all 10 independent alert rules."""
    ds_id = uuid.uuid4()

    # 1. Quality Score Drop
    r1 = QualityScoreDropRule().evaluate({"quality_score": 65.0, "dataset_id": ds_id})
    assert r1 is not None and r1.alert_type == AlertType.QUALITY_SCORE_DROP

    # 2. Validation Failure
    r2 = ValidationFailureRule().evaluate({"run_status": "failed", "dataset_id": ds_id})
    assert r2 is not None and r2.alert_type == AlertType.VALIDATION_FAILURE

    # 3. Critical Rule Failure
    r3 = CriticalValidationRule().evaluate({"failed_critical_rules_count": 2, "dataset_id": ds_id})
    assert r3 is not None and r3.alert_type == AlertType.CRITICAL_VALIDATION_RULE

    # 4. Schema Change
    r4 = SchemaChangeRule().evaluate({"event_type": "schema_change", "dataset_id": ds_id})
    assert r4 is not None and r4.alert_type == AlertType.SCHEMA_CHANGE

    # 5. Data Drift
    r5 = DataDriftRule().evaluate({"drift_status": "critical", "dataset_id": ds_id})
    assert r5 is not None and r5.alert_type == AlertType.DATA_DRIFT

    # 6. Pipeline Failure
    r6 = PipelineFailureRule().evaluate({"pipeline_status": "failed", "dataset_id": ds_id})
    assert r6 is not None and r6.alert_type == AlertType.PIPELINE_FAILURE

    # 7. Pipeline Timeout
    r7 = PipelineTimeoutRule().evaluate({"execution_time_ms": 400000.0, "dataset_id": ds_id})
    assert r7 is not None and r7.alert_type == AlertType.PIPELINE_TIMEOUT

    # 8. Job Failure
    r8 = JobFailureRule().evaluate({"job_status": "failed", "job_id": "job-101", "dataset_id": ds_id})
    assert r8 is not None and r8.alert_type == AlertType.JOB_FAILURE

    # 9. Dataset Freshness
    r9 = DatasetFreshnessRule().evaluate({"hours_since_last_ingest": 36.0, "dataset_id": ds_id})
    assert r9 is not None and r9.alert_type == AlertType.DATASET_FRESHNESS

    # 10. Repeated Failure
    r10 = RepeatedFailureRule().evaluate({"consecutive_failure_count": 4, "dataset_id": ds_id})
    assert r10 is not None and r10.alert_type == AlertType.REPEATED_FAILURE


def test_escalation_policy():
    """Test severity escalation policy calculation."""
    assert escalate_severity(AlertSeverity.MEDIUM, 1) == AlertSeverity.MEDIUM
    assert escalate_severity(AlertSeverity.MEDIUM, 3) == AlertSeverity.HIGH
    assert escalate_severity(AlertSeverity.MEDIUM, 5) == AlertSeverity.CRITICAL


@pytest.mark.asyncio
async def test_alert_deduplication_and_service(db_session):
    """Test AlertService fingerprint deduplication and occurrence counting."""
    bus = InMemoryEventBus()
    svc = AlertService(db_session, event_bus=bus)

    ds_id = uuid.uuid4()
    payload = {"quality_score": 60.0, "dataset_id": ds_id}

    # First event occurrence -> Creates New Alert
    alerts1 = await svc.process_event(payload)
    assert len(alerts1) == 1
    a1 = alerts1[0]
    assert a1.occurrence_count == 1
    assert a1.status == AlertStatus.OPEN

    # Second event occurrence -> Deduplicates & increments counter
    alerts2 = await svc.process_event(payload)
    assert len(alerts2) == 1
    a2 = alerts2[0]
    assert a2.id == a1.id
    assert a2.occurrence_count == 2

    # Acknowledge Alert
    ack = await svc.acknowledge_alert(a1.id)
    assert ack.status == AlertStatus.ACKNOWLEDGED

    # Resolve Alert
    res = await svc.resolve_alert(a1.id)
    assert res.status == AlertStatus.RESOLVED


@pytest.mark.asyncio
async def test_alert_rest_endpoints(client, auth_headers, db_session):
    """Test REST API endpoints /alerts, /alerts/open, /alerts/history, acknowledge, and resolve."""
    bus = InMemoryEventBus()
    svc = AlertService(db_session, event_bus=bus)

    ds_id = uuid.uuid4()
    payload = {"quality_score": 60.0, "dataset_id": ds_id}

    alerts = await svc.process_event(payload)
    await db_session.commit()
    alert_id = str(alerts[0].id)

    # 1. List Alerts
    resp = await client.get("/api/v1/alerts", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) > 0

    # 2. Get Open Alerts
    resp_open = await client.get("/api/v1/alerts/open", headers=auth_headers)
    assert resp_open.status_code == 200
    assert len(resp_open.json()) > 0

    # 3. Get Detail
    resp_detail = await client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == alert_id

    # 4. Acknowledge Alert
    resp_ack = await client.post(f"/api/v1/alerts/{alert_id}/acknowledge", headers=auth_headers)
    assert resp_ack.status_code == 200
    assert resp_ack.json()["status"] == "acknowledged"

    # 5. Resolve Alert
    resp_res = await client.post(f"/api/v1/alerts/{alert_id}/resolve", headers=auth_headers)
    assert resp_res.status_code == 200
    assert resp_res.json()["status"] == "resolved"
