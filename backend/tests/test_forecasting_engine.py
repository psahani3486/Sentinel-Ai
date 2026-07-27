"""
Sentinel AI — Phase 4C Predictive Forecasting Engine Test Suite

Tests all 4 mathematical models (SMA, WMA, EMA, Linear Regression),
8 forecasting strategies, ForecastEngine, ForecastService, and REST API endpoints.
"""

import uuid
import pytest

from app.forecasting.base_strategy import ForecastContext
from app.forecasting.engine import ForecastEngine
from app.forecasting.models import (
    ExponentialSmoothingModel,
    LinearRegressionModel,
    SimpleMovingAverageModel,
    WeightedMovingAverageModel,
)
from app.forecasting.strategies import (
    AlertVolumeForecastStrategy,
    ConnectorReliabilityForecastStrategy,
    DataDriftTrendStrategy,
    DatasetFreshnessForecastStrategy,
    JobFailureProbabilityStrategy,
    PipelineFailureProbabilityStrategy,
    QualityScoreTrendStrategy,
    ValidationFailureProbabilityStrategy,
)
from app.models.enums import ForecastType
from app.services.forecast_service import ForecastService


# ── Model Tests ────────────────────────────────────────────────────────────────
def test_all_4_statistical_models():
    """Test SMA, WMA, EMA, and Linear Regression mathematical forecasting models."""
    series = [95.0, 93.0, 91.0, 89.0, 87.0]

    # 1. Simple Moving Average
    sma = SimpleMovingAverageModel().predict(series, horizon_steps=7)
    assert sma.predicted_value > 0.0

    # 2. Weighted Moving Average
    wma = WeightedMovingAverageModel().predict(series, horizon_steps=7)
    assert wma.predicted_value > 0.0

    # 3. Exponential Smoothing
    ema = ExponentialSmoothingModel(alpha=0.3).predict(series, horizon_steps=7)
    assert ema.predicted_value > 0.0

    # 4. Linear Regression
    lr = LinearRegressionModel().predict(series, horizon_steps=7)
    assert lr.slope < 0.0  # Downward slope
    assert lr.confidence_interval_lower <= lr.predicted_value <= lr.confidence_interval_upper


# ── Strategy Tests ─────────────────────────────────────────────────────────────
def test_all_8_forecasting_strategies():
    """Test execution of all 8 independent forecasting strategies."""
    ds_id = uuid.uuid4()
    ctx = ForecastContext(
        forecast_type=ForecastType.QUALITY_SCORE_TREND,
        dataset_id=ds_id,
        historical_series=[95.0, 92.0, 90.0, 88.0, 85.0],
        horizon_days=7,
    )

    # 1. Quality Score
    f1 = QualityScoreTrendStrategy().generate(ctx)
    assert f1.forecast_type == ForecastType.QUALITY_SCORE_TREND

    # 2. Data Drift
    f2 = DataDriftTrendStrategy().generate(ctx)
    assert f2.forecast_type == ForecastType.DATA_DRIFT_TREND

    # 3. Validation Failure
    f3 = ValidationFailureProbabilityStrategy().generate(ctx)
    assert f3.forecast_type == ForecastType.VALIDATION_FAILURE_PROBABILITY

    # 4. Pipeline Failure
    f4 = PipelineFailureProbabilityStrategy().generate(ctx)
    assert f4.forecast_type == ForecastType.PIPELINE_FAILURE_PROBABILITY

    # 5. Job Failure
    f5 = JobFailureProbabilityStrategy().generate(ctx)
    assert f5.forecast_type == ForecastType.JOB_FAILURE_PROBABILITY

    # 6. Freshness
    f6 = DatasetFreshnessForecastStrategy().generate(ctx)
    assert f6.forecast_type == ForecastType.DATASET_FRESHNESS_FORECAST

    # 7. Alert Volume
    f7 = AlertVolumeForecastStrategy().generate(ctx)
    assert f7.forecast_type == ForecastType.ALERT_VOLUME_FORECAST

    # 8. Connector Reliability
    f8 = ConnectorReliabilityForecastStrategy().generate(ctx)
    assert f8.forecast_type == ForecastType.CONNECTOR_RELIABILITY_FORECAST


def test_forecast_engine():
    """Test ForecastEngine execution pipeline."""
    engine = ForecastEngine()
    ctx = ForecastContext(
        forecast_type=ForecastType.QUALITY_SCORE_TREND,
        dataset_id=uuid.uuid4(),
        historical_series=[95.0, 90.0, 85.0],
    )
    res = engine.run_forecast(ctx)
    assert res.execution_time_ms >= 0.0
    assert len(res.datapoints) > 0


@pytest.mark.asyncio
async def test_forecast_service_and_rest_api(client, auth_headers, db_session):
    """Test ForecastService and REST API endpoints /forecast/run, /history, and /{id}."""
    svc = ForecastService(db_session)
    ds_id = uuid.uuid4()

    run = await svc.run_forecast(
        forecast_type=ForecastType.QUALITY_SCORE_TREND,
        dataset_id=ds_id,
        historical_series=[95.0, 93.0, 91.0],
    )
    await db_session.commit()
    run_id = str(run.id)

    # 1. Run via POST
    resp_post = await client.post(
        "/api/v1/forecast/run",
        headers=auth_headers,
        json={
            "forecast_type": "pipeline_failure_probability",
            "dataset_id": str(ds_id),
            "horizon_days": 14,
        },
    )
    assert resp_post.status_code == 201
    assert resp_post.json()["forecast_type"] == "pipeline_failure_probability"

    # 2. Get History via GET
    resp_hist = await client.get("/api/v1/forecast/history", headers=auth_headers)
    assert resp_hist.status_code == 200
    assert len(resp_hist.json()) >= 2

    # 3. Get Detail via GET
    resp_detail = await client.get(f"/api/v1/forecast/{run_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == run_id
