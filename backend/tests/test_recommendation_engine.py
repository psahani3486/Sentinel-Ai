"""
Sentinel AI — Phase 4B AI Recommendation Engine Test Suite

Tests all 10 recommendation strategies, priority scoring algorithm, hybrid RecommendationEngine,
RecommendationService, and REST API endpoints.
"""

import uuid
import pytest

from app.models.enums import RecommendationCategory, RecommendationPriority
from app.recommendation_engine.base_strategy import RecommendationContext
from app.recommendation_engine.engine import RecommendationEngine, calculate_priority_score
from app.recommendation_engine.strategies import (
    AlertCorrelationRecommendationStrategy,
    ConnectorFailureRecommendationStrategy,
    DataDriftRecommendationStrategy,
    JobFailureRecommendationStrategy,
    MissingValuesRecommendationStrategy,
    OutlierDetectionRecommendationStrategy,
    PipelineFailureRecommendationStrategy,
    QualityScoreDropRecommendationStrategy,
    SchemaChangeRecommendationStrategy,
    ValidationFailureRecommendationStrategy,
)
from app.services.recommendation_service import RecommendationService


# ── Strategy Tests ─────────────────────────────────────────────────────────────
def test_all_10_recommendation_strategies():
    """Test generation of all 10 independent remediation strategies."""
    ds_id = uuid.uuid4()
    ctx = RecommendationContext(
        category=RecommendationCategory.VALIDATION_FAILURE,
        dataset_id=ds_id,
        rca_affected_components=["air_temp"],
    )

    # 1. Validation Failure
    r1 = ValidationFailureRecommendationStrategy().generate(ctx)
    assert r1.category == RecommendationCategory.VALIDATION_FAILURE
    assert len(r1.suggested_next_steps) > 0

    # 2. Schema Change
    r2 = SchemaChangeRecommendationStrategy().generate(ctx)
    assert r2.category == RecommendationCategory.SCHEMA_CHANGE

    # 3. Data Drift
    r3 = DataDriftRecommendationStrategy().generate(ctx)
    assert r3.category == RecommendationCategory.DATA_DRIFT

    # 4. Pipeline Failure
    r4 = PipelineFailureRecommendationStrategy().generate(ctx)
    assert r4.category == RecommendationCategory.PIPELINE_FAILURE

    # 5. Connector Failure
    r5 = ConnectorFailureRecommendationStrategy().generate(ctx)
    assert r5.category == RecommendationCategory.CONNECTOR_FAILURE

    # 6. Job Failure
    r6 = JobFailureRecommendationStrategy().generate(ctx)
    assert r6.category == RecommendationCategory.JOB_FAILURE

    # 7. Quality Score Drop
    r7 = QualityScoreDropRecommendationStrategy().generate(ctx)
    assert r7.category == RecommendationCategory.QUALITY_SCORE_DROP

    # 8. Alert Correlation
    r8 = AlertCorrelationRecommendationStrategy().generate(ctx)
    assert r8.category == RecommendationCategory.ALERT_CORRELATION

    # 9. Missing Values
    r9 = MissingValuesRecommendationStrategy().generate(ctx)
    assert r9.category == RecommendationCategory.MISSING_VALUES

    # 10. Outlier Detection
    r10 = OutlierDetectionRecommendationStrategy().generate(ctx)
    assert r10.category == RecommendationCategory.OUTLIER_DETECTION


def test_priority_score_calculation():
    """Test priority ranking score computation formula."""
    s1 = calculate_priority_score(RecommendationPriority.CRITICAL, "HIGH", "LOW", 95.0)
    s2 = calculate_priority_score(RecommendationPriority.LOW, "LOW", "HIGH", 50.0)

    # Critical + High Impact + Low Effort + High Confidence should yield highest rank score
    assert s1 > s2
    assert s1 >= 90.0


def test_recommendation_engine():
    """Test hybrid RecommendationEngine execution and prioritization."""
    engine = RecommendationEngine()
    ctx = RecommendationContext(
        category=RecommendationCategory.PIPELINE_FAILURE,
        dataset_id=uuid.uuid4(),
    )
    res = engine.generate_recommendation(ctx)
    assert res.priority_score > 0.0
    assert len(res.suggested_next_steps) > 0


@pytest.mark.asyncio
async def test_recommendation_service_and_rest_api(client, auth_headers, db_session):
    """Test RecommendationService and REST API endpoints /recommendations/generate, /history, and /{id}."""
    svc = RecommendationService(db_session)
    ds_id = uuid.uuid4()

    rec = await svc.generate_recommendations(
        category=RecommendationCategory.VALIDATION_FAILURE,
        dataset_id=ds_id,
    )
    await db_session.commit()
    rec_id = str(rec.id)

    # 1. Generate via POST
    resp_post = await client.post(
        "/api/v1/recommendations/generate",
        headers=auth_headers,
        json={
            "category": "pipeline_failure",
            "dataset_id": str(ds_id),
        },
    )
    assert resp_post.status_code == 201
    assert resp_post.json()["category"] == "pipeline_failure"

    # 2. Get History via GET
    resp_hist = await client.get("/api/v1/recommendations/history", headers=auth_headers)
    assert resp_hist.status_code == 200
    assert len(resp_hist.json()) >= 2

    # 3. Get Detail via GET
    resp_detail = await client.get(f"/api/v1/recommendations/{rec_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == rec_id
