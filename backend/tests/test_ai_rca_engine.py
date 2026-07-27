"""
Sentinel AI — Phase 4A AI Root Cause Analysis Engine Test Suite

Tests all 7 automated analyzers, MockLLMProvider, hybrid RootCauseEngine,
RootCauseService, and REST API endpoints.
"""

import uuid
import pytest

from app.ai.analyzers import (
    AlertCorrelationAnalyzer,
    DataDriftAnalyzer,
    JobFailureAnalyzer,
    PipelineFailureAnalyzer,
    QualityDegradationAnalyzer,
    SchemaChangeAnalyzer,
    ValidationFailureAnalyzer,
)
from app.ai.base_analyzer import AnalysisContext
from app.ai.engine import RootCauseEngine
from app.ai.llm_provider import MockLLMProvider
from app.models.dataset import Dataset, DatasetVersion
from app.models.enums import AnalysisType, DatasetType, RuleType, RunStatus, ValidationSeverity, ValidationStatus
from app.models.validation import ValidationResult, ValidationRun
from app.repositories.dataset_repository import DatasetRepository, DatasetVersionRepository
from app.repositories.validation_repository import ValidationResultRepository, ValidationRunRepository
from app.services.root_cause_service import RootCauseService


# ── Analyzer Strategy Tests ───────────────────────────────────────────────────
def test_all_7_analyzers():
    """Test evaluation of all 7 independent root cause analyzers."""
    ds_id = uuid.uuid4()

    # 1. Validation Failure
    ctx1 = AnalysisContext(
        analysis_type=AnalysisType.VALIDATION_FAILURE,
        target_entity_type="validation_run",
        target_entity_id="vr-101",
        dataset_id=ds_id,
        validation_results=[
            {"rule_type": "invalid_numeric_values", "status": "failed", "column_name": "temp", "message": "Invalid string"},
            {"rule_type": "outliers", "status": "failed", "column_name": "speed", "message": "High outlier"},
        ],
    )
    r1 = ValidationFailureAnalyzer().analyze(ctx1)
    assert "temp" in r1.affected_components or "speed" in r1.affected_components
    assert len(r1.evidences) == 2

    # 2. Data Drift
    ctx2 = AnalysisContext(
        analysis_type=AnalysisType.DATA_DRIFT,
        target_entity_type="drift_run",
        target_entity_id="dr-202",
        dataset_id=ds_id,
        drift_results=[{"column_name": "torque", "detector_type": "psi", "drift_score": 0.25}],
    )
    r2 = DataDriftAnalyzer().analyze(ctx2)
    assert "torque" in r2.affected_components
    assert r2.confidence_score > 80.0

    # 3. Schema Change
    ctx3 = AnalysisContext(
        analysis_type=AnalysisType.SCHEMA_CHANGE,
        target_entity_type="dataset",
        target_entity_id=str(ds_id),
        schema_history=[{"column_name": "status_code", "change_type": "modified", "old_type": "int", "new_type": "str"}],
    )
    r3 = SchemaChangeAnalyzer().analyze(ctx3)
    assert "status_code" in r3.affected_components

    # 4. Alert Correlation
    ctx4 = AnalysisContext(
        analysis_type=AnalysisType.ALERT_CORRELATION,
        target_entity_type="dataset",
        target_entity_id=str(ds_id),
        alerts=[{"alert_type": "quality_score_drop", "title": "Score Drop"}],
    )
    r4 = AlertCorrelationAnalyzer().analyze(ctx4)
    assert r4.confidence_score >= 80.0

    # 5. Pipeline Failure
    r5 = PipelineFailureAnalyzer().analyze(ctx1)
    assert "connector" in r5.affected_components

    # 6. Job Failure
    ctx6 = AnalysisContext(
        analysis_type=AnalysisType.JOB_FAILURE,
        target_entity_type="job",
        target_entity_id="job-99",
        jobs=[{"job_id": "job-99", "status": "failed"}],
    )
    r6 = JobFailureAnalyzer().analyze(ctx6)
    assert "worker" in r6.affected_components

    # 7. Quality Degradation
    r7 = QualityDegradationAnalyzer().analyze(ctx1)
    assert r7.confidence_score >= 90.0


def test_mock_llm_provider():
    """Test MockLLMProvider deterministic offline explanation synthesis."""
    provider = MockLLMProvider()
    explanation = provider.generate_explanation("prompt", {"analysis_type": "validation_failure", "target_id": "vr-101"})
    assert "vr-101" in explanation
    assert provider.provider_name == "MockLLMProvider"


def test_root_cause_engine():
    """Test hybrid RootCauseEngine pipeline (rule analysis + LLM explanation)."""
    engine = RootCauseEngine()
    ctx = AnalysisContext(
        analysis_type=AnalysisType.VALIDATION_FAILURE,
        target_entity_type="validation_run",
        target_entity_id="vr-999",
        validation_results=[{"rule_type": "missing_values", "status": "failed", "column_name": "id"}],
    )
    report = engine.run_root_cause_analysis(ctx)
    assert "vr-999" in report.summary
    assert report.confidence_score > 0.0
    assert report.llm_provider_name == "MockLLMProvider"


@pytest.mark.asyncio
async def test_root_cause_service_validation_telemetry(db_session, test_user):
    """Test RootCauseService telemetry gathering from real ValidationRun database entities."""
    dataset_repo = DatasetRepository(db_session)
    run_repo = ValidationRunRepository(db_session)
    result_repo = ValidationResultRepository(db_session)

    version_repo = DatasetVersionRepository(db_session)

    ds = await dataset_repo.create(
        Dataset(name="Telemetry Dataset", dataset_type=DatasetType.TABULAR, owner_id=test_user.id)
    )

    ver = await version_repo.create(
        DatasetVersion(dataset_id=ds.id, version_number=1, storage_path="/tmp/v1.csv", ingested_by_id=test_user.id)
    )

    vr = await run_repo.create(
        ValidationRun(
            dataset_id=ds.id,
            dataset_version_id=ver.id,
            status=RunStatus.FAILED,
        )
    )

    await result_repo.create(
        ValidationResult(
            validation_run_id=vr.id,
            rule_type=RuleType.MISSING_VALUES,
            status=ValidationStatus.FAILED,
            severity=ValidationSeverity.HIGH,
            affected_columns=["sensor_temp"],
            message="Found 12 null values",
        )
    )
    await db_session.commit()

    svc = RootCauseService(db_session)
    rca = await svc.run_root_cause_analysis(
        analysis_type=AnalysisType.VALIDATION_FAILURE,
        target_entity_type="validation_run",
        target_entity_id=str(vr.id),
        dataset_id=ds.id,
    )
    assert rca.confidence_score > 0.0
    assert len(rca.evidences) > 0


@pytest.mark.asyncio
async def test_root_cause_service_and_rest_api(client, auth_headers, db_session):
    """Test RootCauseService execution and REST API endpoints /analysis/root-cause, /history, and /{id}."""
    svc = RootCauseService(db_session)
    ds_id = uuid.uuid4()

    # Service execution
    rca = await svc.run_root_cause_analysis(
        analysis_type=AnalysisType.VALIDATION_FAILURE,
        target_entity_type="validation_run",
        target_entity_id="vr-api-test",
        dataset_id=ds_id,
    )
    await db_session.commit()
    rca_id = str(rca.id)

    # 1. Trigger Analysis via POST
    resp_post = await client.post(
        "/api/v1/analysis/root-cause",
        headers=auth_headers,
        json={
            "analysis_type": "data_drift",
            "target_entity_type": "drift_run",
            "target_entity_id": "dr-api-test",
            "dataset_id": str(ds_id),
        },
    )
    assert resp_post.status_code == 201
    data_post = resp_post.json()
    assert data_post["analysis_type"] == "data_drift"

    # 2. Get History via GET
    resp_hist = await client.get("/api/v1/analysis/history", headers=auth_headers)
    assert resp_hist.status_code == 200
    assert len(resp_hist.json()) >= 2

    # 3. Get Detail via GET
    resp_detail = await client.get(f"/api/v1/analysis/{rca_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == rca_id
