"""
Sentinel AI — Phase 7B Enterprise Policy Engine Test Suite

Tests 10 Policy Specification Rules, PolicyExecutor, PolicyEngine, PolicyReporter,
PolicyService, and REST API endpoints.
"""

import pytest

from app.policies.engine import PolicyEngine
from app.policies.policies import (
    CatalogGovernancePolicy,
    DatasetGovernancePolicy,
    DriftThresholdPolicy,
    IncidentEscalationPolicy,
    PluginPolicy,
    QualityThresholdPolicy,
    RetentionPolicy,
    SchemaPolicy,
    ValidationPolicy,
    WorkflowPolicy,
)
from app.policies.reporter import PolicyReporter
from app.services.policy_service import PolicyService


# ── Policy Rule Specification Tests ─────────────────────────────────────────────
def test_all_ten_policy_specifications():
    """Test Specification Pattern evaluations for all 10 policy rules."""
    # 1. Dataset Governance Policy
    p1 = DatasetGovernancePolicy()
    assert p1.is_satisfied_by({"owner": "Team A", "steward": "Lead B"}) is True
    assert p1.is_satisfied_by({}) is False

    # 2. Schema Policy
    p2 = SchemaPolicy()
    assert p2.is_satisfied_by({"dropped_columns": []}) is True
    assert p2.is_satisfied_by({"dropped_columns": ["col_a"]}) is False

    # 3. Validation Policy
    p3 = ValidationPolicy()
    assert p3.is_satisfied_by({"critical_failed_count": 0}) is True
    assert p3.is_satisfied_by({"critical_failed_count": 2}) is False

    # 4. Quality Threshold Policy
    p4 = QualityThresholdPolicy()
    assert p4.is_satisfied_by({"quality_score": 95.0}) is True
    assert p4.is_satisfied_by({"quality_score": 85.0}) is False

    # 5. Drift Threshold Policy
    p5 = DriftThresholdPolicy()
    assert p5.is_satisfied_by({"max_psi": 0.10}) is True
    assert p5.is_satisfied_by({"max_psi": 0.35}) is False

    # 6. Workflow Policy
    p6 = WorkflowPolicy()
    assert p6.is_satisfied_by({"duration_seconds": 120}) is True
    assert p6.is_satisfied_by({"duration_seconds": 450}) is False

    # 7. Plugin Policy
    p7 = PluginPolicy()
    assert p7.is_satisfied_by({"permissions": ["read_dataset"]}) is True
    assert p7.is_satisfied_by({"permissions": ["root_access"]}) is False

    # 8. Catalog Governance Policy
    p8 = CatalogGovernancePolicy()
    assert p8.is_satisfied_by({"sensitivity": "confidential"}) is True
    assert p8.is_satisfied_by({"sensitivity": "invalid_tier"}) is False

    # 9. Retention Policy
    p9 = RetentionPolicy()
    assert p9.is_satisfied_by({"retention_days": 180}) is True
    assert p9.is_satisfied_by({"retention_days": 730}) is False

    # 10. Incident Escalation Policy
    p10 = IncidentEscalationPolicy()
    assert p10.is_satisfied_by({"severity": "critical", "open_hours": 1}) is True
    assert p10.is_satisfied_by({"severity": "critical", "open_hours": 5}) is False


def test_policy_engine_executor_and_reporter():
    """Test PolicyExecutor, PolicyEngine, and PolicyReporter."""
    engine = PolicyEngine()
    results = engine.evaluate_suite({"owner": "Data Ops", "steward": "Lead", "quality_score": 92.0})
    assert len(results) == 10

    reporter = PolicyReporter()
    summary = reporter.build_compliance_summary(results)
    assert summary["total_policies_evaluated"] == 10


@pytest.mark.asyncio
async def test_policy_service_and_rest_api(client, auth_headers, db_session):
    """Test PolicyService and REST API endpoints POST /policies/evaluate, GET /policies, GET /policies/{id}, and GET /policies/evaluations."""
    svc = PolicyService(db_session)
    definitions = await svc.seed_initial_policies()
    await db_session.commit()
    assert len(definitions) == 10

    policy_uuid = str(definitions[0].id)

    # 1. Evaluate Policies via POST
    resp_eval = await client.post(
        "/api/v1/policies/evaluate",
        json={"target": {"owner": "Data Team", "steward": "Officer", "quality_score": 95.0}},
        headers=auth_headers,
    )
    assert resp_eval.status_code == 200
    assert len(resp_eval.json()) == 10

    # 2. Get Policy Definitions via GET
    resp_defs = await client.get("/api/v1/policies", headers=auth_headers)
    assert resp_defs.status_code == 200
    assert len(resp_defs.json()) == 10

    # 3. Get Policy Detail via GET
    resp_detail = await client.get(f"/api/v1/policies/{policy_uuid}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == policy_uuid

    # 4. Get Evaluations via GET
    resp_evals = await client.get("/api/v1/policies/evaluations", headers=auth_headers)
    assert resp_evals.status_code == 200
    assert len(resp_evals.json()) >= 10
