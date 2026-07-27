"""
Sentinel AI — Forecast Strategy Registry

Registry Pattern mapping ForecastType enums to concrete strategy instances.
"""

import logging

from app.forecasting.base_strategy import BaseForecastStrategy
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

logger = logging.getLogger(__name__)


class ForecastRegistry:
    """Registry maintaining instances of all predictive forecasting strategies."""

    def __init__(self) -> None:
        self._strategies: dict[ForecastType, BaseForecastStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default 8 forecasting strategies."""
        strategies = [
            QualityScoreTrendStrategy(),
            DataDriftTrendStrategy(),
            ValidationFailureProbabilityStrategy(),
            PipelineFailureProbabilityStrategy(),
            JobFailureProbabilityStrategy(),
            DatasetFreshnessForecastStrategy(),
            AlertVolumeForecastStrategy(),
            ConnectorReliabilityForecastStrategy(),
        ]
        for s in strategies:
            self.register(s)

    def register(self, strategy: BaseForecastStrategy) -> None:
        """Register a forecasting strategy."""
        self._strategies[strategy.forecast_type] = strategy
        logger.debug("Registered Forecast Strategy: %s", strategy.forecast_type.value)

    def get(self, forecast_type: ForecastType) -> BaseForecastStrategy:
        """Retrieve strategy by ForecastType."""
        strat = self._strategies.get(forecast_type)
        if not strat:
            return QualityScoreTrendStrategy()
        return strat

    def get_all(self) -> list[BaseForecastStrategy]:
        """Return list of all registered strategies."""
        return list(self._strategies.values())


# Global default registry singleton
_default_registry: ForecastRegistry | None = None


def get_forecast_registry() -> ForecastRegistry:
    """Return singleton ForecastRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ForecastRegistry()
    return _default_registry
