"""
Sentinel AI — Phase 3D Data Drift Engine Test Suite

Tests all 10 statistical drift detectors, column type auto-inference,
DriftRegistry, DriftExecutor, DriftEngine, DriftService persistence, and REST APIs.
"""

import pytest

from app.drift_engine.detectors import (
    CardinalityDriftDetector,
    CategoryDistributionDetector,
    JensenShannonDetector,
    KLDivergenceDetector,
    MeanDriftDetector,
    MissingValueDriftDetector,
    NumericDistributionDetector,
    PSIDetector,
    StdDriftDetector,
    WassersteinDetector,
)
from app.drift_engine.engine import DriftEngine
from app.drift_engine.executor import DriftExecutor, infer_column_type
from app.drift_engine.registry import DriftRegistry
from app.models.dataset import Dataset, DatasetVersion
from app.models.enums import DatasetType, DetectorType, DriftStatus
from app.repositories.dataset_repository import DatasetRepository, DatasetVersionRepository
from app.repositories.drift_repository import DriftRunRepository
from app.services.drift_service import DriftService


# ── Detector Tests ─────────────────────────────────────────────────────────────
def test_all_10_detectors():
    """Test execution of all 10 independent drift detectors."""
    base_num = [10.0, 12.0, 11.5, 13.0, 12.2, 11.8, 10.5, 12.1]
    curr_num_drifted = [30.0, 35.0, 32.0, 31.5, 34.0, 33.2, 36.0, 35.5]

    # 1. PSI
    psi_res = PSIDetector().detect(base_num, curr_num_drifted, "temp")
    assert psi_res.detector_type == DetectorType.PSI
    assert psi_res.drift_detected is True

    # 2. Jensen-Shannon
    js_res = JensenShannonDetector().detect(base_num, curr_num_drifted, "temp")
    assert js_res.detector_type == DetectorType.JENSEN_SHANNON
    assert js_res.drift_detected is True

    # 3. KL Divergence
    kl_res = KLDivergenceDetector().detect(base_num, curr_num_drifted, "temp")
    assert kl_res.detector_type == DetectorType.KL_DIVERGENCE
    assert kl_res.drift_detected is True

    # 4. Wasserstein
    w_res = WassersteinDetector().detect(base_num, curr_num_drifted, "temp")
    assert w_res.detector_type == DetectorType.WASSERSTEIN
    assert w_res.drift_detected is True

    # 5. Mean Drift
    m_res = MeanDriftDetector().detect(base_num, curr_num_drifted, "temp")
    assert m_res.detector_type == DetectorType.MEAN_DRIFT
    assert m_res.drift_detected is True

    # 6. Std Drift
    std_res = StdDriftDetector().detect([10.0, 10.1, 10.2], [10.0, 50.0, 100.0], "temp")
    assert std_res.detector_type == DetectorType.STD_DRIFT
    assert std_res.drift_detected is True

    # 7. Missing Value Drift
    null_res = MissingValueDriftDetector().detect([1, 2, None, 4], [None, None, None, 4], "temp")
    assert null_res.detector_type == DetectorType.MISSING_VALUE_DRIFT
    assert null_res.drift_detected is True

    # 8. Cardinality Drift
    card_res = CardinalityDriftDetector().detect(["a", "b"], ["a", "b", "c", "d", "e"], "cat")
    assert card_res.detector_type == DetectorType.CARDINALITY_DRIFT
    assert card_res.drift_detected is True

    # 9. Category Distribution
    cat_res = CategoryDistributionDetector().detect(["a", "a", "a"], ["b", "b", "b"], "cat")
    assert cat_res.detector_type == DetectorType.CATEGORY_DISTRIBUTION_DRIFT
    assert cat_res.drift_detected is True

    # 10. Numeric Distribution
    num_dist_res = NumericDistributionDetector().detect(base_num, curr_num_drifted, "temp")
    assert num_dist_res.detector_type == DetectorType.NUMERIC_DISTRIBUTION_DRIFT
    assert num_dist_res.drift_detected is True


def test_column_type_inference_and_executor():
    """Test column type auto-inference and compatible detector filtering."""
    assert infer_column_type([1.5, 2.3, 4.0]) == "numeric"
    assert infer_column_type(["RUNNING", "IDLE", "STOPPED"]) == "categorical"
    assert infer_column_type([True, False, True]) == "boolean"

    reg = DriftRegistry()
    executor = DriftExecutor(registry=reg)

    num_dets = executor.get_compatible_detector_types("numeric")
    assert len(num_dets) == 8

    cat_dets = executor.get_compatible_detector_types("categorical")
    assert len(cat_dets) == 3


def test_drift_engine_execution():
    """Test DriftEngine multi-column analysis and dataset status score."""
    engine = DriftEngine()

    base_ds = {
        "temp": [20.0, 21.0, 20.5, 22.0],
        "status": ["OK", "OK", "OK", "OK"],
    }
    curr_ds = {
        "temp": [50.0, 52.0, 51.5, 53.0],  # Drifted
        "status": ["OK", "OK", "OK", "OK"],
    }

    res = engine.run_drift_analysis(base_ds, curr_ds)

    assert res["status"] in (DriftStatus.HIGH, DriftStatus.CRITICAL, DriftStatus.MEDIUM)
    assert res["overall_drift_score"] > 0.0
    assert len(res["results"]) > 0


@pytest.mark.asyncio
async def test_drift_service_run_and_persist(db_session, test_user):
    """Test DriftService executing drift detection and persisting run to database."""
    dataset_repo = DatasetRepository(db_session)
    version_repo = DatasetVersionRepository(db_session)

    dataset = await dataset_repo.create(
        Dataset(
            name="Drift Test Asset",
            description="Test dataset",
            dataset_type=DatasetType.TABULAR,
            owner_id=test_user.id,
        )
    )

    version1 = await version_repo.create(
        DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/tmp/v1.csv",
            file_size_bytes=1000,
            row_count=100,
            column_count=5,
            ingested_by_id=test_user.id,
        )
    )

    version2 = await version_repo.create(
        DatasetVersion(
            dataset_id=dataset.id,
            version_number=2,
            storage_path="/tmp/v2.csv",
            file_size_bytes=1000,
            row_count=100,
            column_count=5,
            ingested_by_id=test_user.id,
        )
    )

    svc = DriftService(db_session)
    drift_run = await svc.run_drift_detection(
        dataset_id=dataset.id,
        current_version_id=version2.id,
        baseline_version_id=version1.id,
    )

    assert drift_run.id is not None
    assert drift_run.dataset_id == dataset.id
    assert len(drift_run.results) > 0

    run_repo = DriftRunRepository(db_session)
    fetched = await run_repo.get_by_id_with_results(drift_run.id)
    assert fetched is not None
    assert len(fetched.results) == len(drift_run.results)


@pytest.mark.asyncio
async def test_drift_rest_endpoints(client, auth_headers, db_session, test_user):
    """Test REST API endpoints /datasets/{id}/drift, drift-history, and /drift/{id}."""
    dataset_repo = DatasetRepository(db_session)
    version_repo = DatasetVersionRepository(db_session)

    dataset = await dataset_repo.create(
        Dataset(
            name="REST Drift Dataset",
            description="Test dataset",
            dataset_type=DatasetType.TABULAR,
            owner_id=test_user.id,
        )
    )

    v1 = await version_repo.create(
        DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/tmp/v1.csv",
            ingested_by_id=test_user.id,
        )
    )

    v2 = await version_repo.create(
        DatasetVersion(
            dataset_id=dataset.id,
            version_number=2,
            storage_path="/tmp/v2.csv",
            ingested_by_id=test_user.id,
        )
    )
    await db_session.commit()

    # 1. Trigger Drift
    resp = await client.post(
        f"/api/v1/datasets/{dataset.id}/drift",
        headers=auth_headers,
        json={
            "current_version_id": str(v2.id),
            "baseline_version_id": str(v1.id),
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    run_id = data["id"]
    assert data["dataset_id"] == str(dataset.id)

    # 2. Get Drift History
    resp_hist = await client.get(f"/api/v1/datasets/{dataset.id}/drift-history", headers=auth_headers)
    assert resp_hist.status_code == 200
    hist_list = resp_hist.json()
    assert len(hist_list) == 1

    # 3. Get Drift Detail
    resp_detail = await client.get(f"/api/v1/drift/{run_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert detail["id"] == run_id
    assert len(detail["results"]) > 0
