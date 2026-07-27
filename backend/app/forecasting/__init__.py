"""Forecasting Engine Package."""

from app.forecasting.base_strategy import (
    BaseForecastStrategy,
    ForecastContext,
    ForecastDatapoint,
    RawForecastCandidate,
)
from app.forecasting.engine import ForecastEngine, ProcessedForecastResult
from app.forecasting.executor import ForecastExecutor
from app.forecasting.models import (
    BaseForecastModel,
    ExponentialSmoothingModel,
    ForecastModelOutput,
    LinearRegressionModel,
    SimpleMovingAverageModel,
    WeightedMovingAverageModel,
)
from app.forecasting.registry import ForecastRegistry, get_forecast_registry
from app.forecasting.reporter import ForecastReporter
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

__all__ = [
    "BaseForecastStrategy",
    "ForecastContext",
    "ForecastDatapoint",
    "RawForecastCandidate",
    "BaseForecastModel",
    "ForecastModelOutput",
    "SimpleMovingAverageModel",
    "WeightedMovingAverageModel",
    "ExponentialSmoothingModel",
    "LinearRegressionModel",
    "ForecastRegistry",
    "get_forecast_registry",
    "ForecastExecutor",
    "ForecastEngine",
    "ProcessedForecastResult",
    "ForecastReporter",
    "QualityScoreTrendStrategy",
    "DataDriftTrendStrategy",
    "ValidationFailureProbabilityStrategy",
    "PipelineFailureProbabilityStrategy",
    "JobFailureProbabilityStrategy",
    "DatasetFreshnessForecastStrategy",
    "AlertVolumeForecastStrategy",
    "ConnectorReliabilityForecastStrategy",
]
