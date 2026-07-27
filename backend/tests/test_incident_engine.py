"""
Sentinel AI — Phase 5A Unified Incident Workspace Test Suite

Tests all 5 signal correlators, chronological timeline ordering,
IncidentEngine, IncidentService, and REST API endpoints.
"""

import uuid
import pytest

from app.incidents.base_correlator import IncidentContext
from app.incidents.correlators import (
    AIAnalysisIncidentCorrelator,
    AlertIncidentCorrelator,
    DriftIncidentCorrelator,
    SchemaIncidentCorrelator,
    ValidationIncidentCorrelator,
)
from app.incidents.engine import IncidentEngine
from app.models.enums import IncidentSeverity
from app.services.incident_service import IncidentService


# ── Correlator Tests ───────────────────────────────────────────────────────────
def test_all_5_signal_correlators():
    """Test multi-signal telemetry correlator strategies."""
    ds_id = uuid.uuid4()
    ctx = IncidentContext(
        dataset_id=ds_id,
        title="Telemetry Signal Test Incident",
        telemetry_signals={
            "validation_results": [{"rule_type": "missing_values", "column_name": "temp", "message": "12 nulls"}],
            "drift_results": [{"feature_name": "temp", "psi_value": 0.18}],
            "schema_changes": [{"change_description": "Column added"}],
            "alerts": [{"id": "alt-1", "title": "SLA Breach"}],
            "rca": {"id": "rca-1", "probable_root_cause": "Malformed string"},
            "recommendation": {"id": "rec-1", "title": "Cast strings"},
            "forecast": {"id": "fc-1", "summary": "Quality drop projected"},
        },
    )

    # 1. Validation Correlator
    e1 = ValidationIncidentCorrelator().correlate(ctx)
    assert len(e1) == 1

    # 2. Drift Correlator
    e2 = DriftIncidentCorrelator().correlate(ctx)
    assert len(e2) == 1

    # 3. Schema Correlator
    e3 = SchemaIncidentCorrelator().correlate(ctx)
    assert len(e3) == 1

    # 4. Alert Correlator
    e4 = AlertIncidentCorrelator().correlate(ctx)
    assert len(e4) == 1

    # 5. AI Analysis Correlator
    e5 = AIAnalysisIncidentCorrelator().correlate(ctx)
    assert len(e5) == 3  # RCA, Recommendation, Forecast


def test_incident_engine_and_timeline_sorting():
    """Test IncidentEngine multi-signal correlation and chronological timeline sorting."""
    engine = IncidentEngine()
    ctx = IncidentContext(
        dataset_id=uuid.uuid4(),
        title="Chronological Timeline Correlation Test",
        telemetry_signals={
            "validation_results": [{"rule_type": "missing_values", "message": "Failed"}],
            "alerts": [{"title": "Critical Alert"}],
        },
    )
    candidate = engine.create_incident(ctx)
    assert len(candidate.timeline_events) >= 2

    # Verify timeline is sorted chronologically asc
    timestamps = [e.timestamp for e in candidate.timeline_events]
    assert timestamps == sorted(timestamps)


@pytest.mark.asyncio
async def test_incident_service_and_rest_api(client, auth_headers, db_session):
    """Test IncidentService and REST API endpoints /incidents/create, /, /{id}, and /{id}/timeline."""
    svc = IncidentService(db_session)
    ds_id = uuid.uuid4()

    inc = await svc.create_incident(
        title="Industrial Sensor Incident Workspace",
        dataset_id=ds_id,
        severity=IncidentSeverity.CRITICAL,
        telemetry_signals={"validation_results": [{"rule_type": "missing_values"}]},
    )
    await db_session.commit()
    inc_id = str(inc.id)

    # 1. Create via POST
    resp_post = await client.post(
        "/api/v1/incidents/create",
        headers=auth_headers,
        json={
            "title": "Pipeline Ingestion Socket Failure",
            "dataset_id": str(ds_id),
            "severity": "critical",
        },
    )
    assert resp_post.status_code == 201
    assert resp_post.json()["title"] == "Pipeline Ingestion Socket Failure"

    # 2. Get List via GET
    resp_list = await client.get("/api/v1/incidents", headers=auth_headers)
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 2

    # 3. Get Detail via GET
    resp_detail = await client.get(f"/api/v1/incidents/{inc_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == inc_id

    # 4. Get Timeline via GET
    resp_tl = await client.get(f"/api/v1/incidents/{inc_id}/timeline", headers=auth_headers)
    assert resp_tl.status_code == 200
    assert len(resp_tl.json()) >= 1
