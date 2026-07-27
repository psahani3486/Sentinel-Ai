"""
Sentinel AI — Automated Predictive Forecasting Strategies

Implements 8 independent forecasting strategies:
1. Quality Score Trend
2. Data Drift Trend
3. Validation Failure Probability
4. Pipeline Failure Probability
5. Job Failure Probability
6. Dataset Freshness Forecast
7. Alert Volume Forecast
8. Connector Reliability Forecast
"""

from app.forecasting.base_strategy import (
    BaseForecastStrategy,
    ForecastContext,
    ForecastDatapoint,
    RawForecastCandidate,
)
from app.forecasting.models import LinearRegressionModel
from app.models.enums import ForecastType, RiskLevel, TrendDirection


# ── Helper function ─────────────────────────────────────────────────────────────
def _determine_trend_and_risk(slope: float, predicted: float, metric_type: str) -> tuple[TrendDirection, RiskLevel]:
    """Helper to derive TrendDirection and RiskLevel from slope and predicted value."""
    if abs(slope) < 0.01:
        direction = TrendDirection.STABLE
    elif slope > 0:
        direction = TrendDirection.UPWARD
    else:
        direction = TrendDirection.DOWNWARD

    if metric_type == "quality_score":
        if predicted < 70.0:
            risk = RiskLevel.CRITICAL
        elif predicted < 85.0:
            risk = RiskLevel.HIGH
        elif predicted < 92.0:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW
    elif metric_type == "probability":
        if predicted > 0.7:
            risk = RiskLevel.CRITICAL
        elif predicted > 0.4:
            risk = RiskLevel.HIGH
        elif predicted > 0.2:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW
    else:
        risk = RiskLevel.MEDIUM if direction == TrendDirection.UPWARD else RiskLevel.LOW

    return direction, risk


# ── 1. Quality Score Trend Strategy ───────────────────────────────────────────
class QualityScoreTrendStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.QUALITY_SCORE_TREND

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [95.0, 93.5, 91.0, 89.2, 87.0]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        direction, risk = _determine_trend_and_risk(out.slope, out.predicted_value, "quality_score")

        dp = ForecastDatapoint(
            target_metric="Quality Score Trend (0-100%)",
            predicted_value=max(0.0, min(100.0, out.predicted_value)),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=min(100.0, out.confidence_interval_upper),
            trend_direction=direction,
            risk_level=risk,
            explanation=f"Data quality score projected at {out.predicted_value:.1f}% in {context.horizon_days} days.",
            preventive_actions=[
                "Deploy quality SLA gate on staging pipeline.",
                "Sanitize incoming missing values on sensor features.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=risk,
            summary=f"Quality score trajectory is {direction.value} over {context.horizon_days}-day horizon.",
            datapoints=[dp],
        )


# ── 2. Data Drift Trend Strategy ───────────────────────────────────────────────
class DataDriftTrendStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.DATA_DRIFT_TREND

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [0.02, 0.05, 0.09, 0.14, 0.19]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        direction, risk = _determine_trend_and_risk(out.slope, out.predicted_value, "probability")

        dp = ForecastDatapoint(
            target_metric="Feature Distribution PSI Drift Metric",
            predicted_value=max(0.0, out.predicted_value),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=max(0.0, out.confidence_interval_upper),
            trend_direction=direction,
            risk_level=risk,
            explanation=f"PSI drift projected to reach {out.predicted_value:.2f} (Threshold: 0.10).",
            preventive_actions=[
                "Re-baseline feature distributions in Data Drift Observatory.",
                "Review upstream sensor calibration.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=risk,
            summary=f"Feature distribution drift is {direction.value}.",
            datapoints=[dp],
        )


# ── 3. Validation Failure Probability Strategy ─────────────────────────────────
class ValidationFailureProbabilityStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.VALIDATION_FAILURE_PROBABILITY

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [0.05, 0.10, 0.18, 0.25, 0.35]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        direction, risk = _determine_trend_and_risk(out.slope, out.predicted_value, "probability")

        dp = ForecastDatapoint(
            target_metric="Validation Rule Failure Probability",
            predicted_value=max(0.0, min(1.0, out.predicted_value)),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=min(1.0, out.confidence_interval_upper),
            trend_direction=direction,
            risk_level=risk,
            explanation=f"Validation failure probability predicted at {out.predicted_value * 100:.1f}%.",
            preventive_actions=[
                "Pre-validate column types prior to DB commit.",
                "Adjust outlier tolerance bounds.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=risk,
            summary=f"Validation failure risk is {risk.value}.",
            datapoints=[dp],
        )


# ── 4. Pipeline Failure Probability Strategy ───────────────────────────────────
class PipelineFailureProbabilityStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.PIPELINE_FAILURE_PROBABILITY

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [0.01, 0.03, 0.05, 0.12, 0.22]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        direction, risk = _determine_trend_and_risk(out.slope, out.predicted_value, "probability")

        dp = ForecastDatapoint(
            target_metric="Pipeline Timeout Failure Probability",
            predicted_value=max(0.0, min(1.0, out.predicted_value)),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=min(1.0, out.confidence_interval_upper),
            trend_direction=direction,
            risk_level=risk,
            explanation=f"Pipeline timeout risk estimated at {out.predicted_value * 100:.1f}%.",
            preventive_actions=[
                "Expand socket connection timeout limits.",
                "Verify database connection credentials in secrets manager.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=risk,
            summary=f"Pipeline failure probability is {direction.value}.",
            datapoints=[dp],
        )


# ── 5. Job Failure Probability Strategy ────────────────────────────────────────
class JobFailureProbabilityStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.JOB_FAILURE_PROBABILITY

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [0.02, 0.04, 0.06, 0.10, 0.15]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        direction, risk = _determine_trend_and_risk(out.slope, out.predicted_value, "probability")

        dp = ForecastDatapoint(
            target_metric="Worker Task Crash Probability",
            predicted_value=max(0.0, min(1.0, out.predicted_value)),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=min(1.0, out.confidence_interval_upper),
            trend_direction=direction,
            risk_level=risk,
            explanation=f"Worker memory overflow crash risk estimated at {out.predicted_value * 100:.1f}%.",
            preventive_actions=[
                "Increase worker process RAM allocation to 4GB.",
                "Adjust worker queue concurrency limits.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=risk,
            summary=f"Worker job failure probability is {direction.value}.",
            datapoints=[dp],
        )


# ── 6. Dataset Freshness Forecast Strategy ─────────────────────────────────────
class DatasetFreshnessForecastStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.DATASET_FRESHNESS_FORECAST

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [1.0, 1.2, 1.5, 2.1, 3.4]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        dp = ForecastDatapoint(
            target_metric="Data Arrival Ingestion Latency (Hours)",
            predicted_value=max(0.0, out.predicted_value),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=max(0.0, out.confidence_interval_upper),
            trend_direction=TrendDirection.UPWARD if out.slope > 0 else TrendDirection.DOWNWARD,
            risk_level=RiskLevel.HIGH if out.predicted_value > 4.0 else RiskLevel.LOW,
            explanation=f"Data arrival latency projected to increase to {out.predicted_value:.1f} hours.",
            preventive_actions=[
                "Check ingestion cron schedule.",
                "Verify source data producer pipeline health.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=dp.risk_level,
            summary=f"Data arrival latency trend is {dp.trend_direction.value}.",
            datapoints=[dp],
        )


# ── 7. Alert Volume Forecast Strategy ──────────────────────────────────────────
class AlertVolumeForecastStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.ALERT_VOLUME_FORECAST

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [5.0, 8.0, 12.0, 18.0, 25.0]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        dp = ForecastDatapoint(
            target_metric="Daily Alert Notification Volume",
            predicted_value=max(0.0, out.predicted_value),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=max(0.0, out.confidence_interval_upper),
            trend_direction=TrendDirection.UPWARD if out.slope > 0 else TrendDirection.DOWNWARD,
            risk_level=RiskLevel.HIGH if out.predicted_value > 20.0 else RiskLevel.LOW,
            explanation=f"Daily alert volume projected at {out.predicted_value:.0f} alerts/day.",
            preventive_actions=[
                "Tune alert deduplication and suppression rules.",
                "Resolve root pipeline connection failures.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=dp.risk_level,
            summary=f"Daily alert volume trajectory is {dp.trend_direction.value}.",
            datapoints=[dp],
        )


# ── 8. Connector Reliability Forecast Strategy ────────────────────────────────
class ConnectorReliabilityForecastStrategy(BaseForecastStrategy):
    @property
    def forecast_type(self) -> ForecastType:
        return ForecastType.CONNECTOR_RELIABILITY_FORECAST

    def generate(self, context: ForecastContext) -> RawForecastCandidate:
        series = context.historical_series or [99.5, 99.1, 98.4, 97.2, 95.8]
        model = LinearRegressionModel()
        out = model.predict(series, context.horizon_days)

        dp = ForecastDatapoint(
            target_metric="Connector Uptime Reliability (0-100%)",
            predicted_value=max(0.0, min(100.0, out.predicted_value)),
            confidence_interval_lower=max(0.0, out.confidence_interval_lower),
            confidence_interval_upper=min(100.0, out.confidence_interval_upper),
            trend_direction=TrendDirection.DOWNWARD if out.slope < 0 else TrendDirection.UPWARD,
            risk_level=RiskLevel.HIGH if out.predicted_value < 95.0 else RiskLevel.LOW,
            explanation=f"Connector uptime reliability projected at {out.predicted_value:.1f}%.",
            preventive_actions=[
                "Update connector driver dependencies.",
                "Re-authenticate API credentials.",
            ],
        )

        return RawForecastCandidate(
            forecast_type=self.forecast_type,
            algorithm_name=model.name,
            overall_risk_level=dp.risk_level,
            summary=f"Connector reliability trend is {dp.trend_direction.value}.",
            datapoints=[dp],
        )
