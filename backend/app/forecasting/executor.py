"""
Sentinel AI — Forecast Executor

Executes matching forecasting strategies against historical telemetry context.
"""

from app.forecasting.base_strategy import ForecastContext, RawForecastCandidate
from app.forecasting.registry import ForecastRegistry, get_forecast_registry


class ForecastExecutor:
    """Executes matching forecasting strategy for a given ForecastContext."""

    def __init__(self, registry: ForecastRegistry | None = None) -> None:
        self._registry = registry or get_forecast_registry()

    def execute_strategy(self, context: ForecastContext) -> RawForecastCandidate:
        """
        Execute strategy matching context.forecast_type.

        Returns:
            RawForecastCandidate.
        """
        strategy = self._registry.get(context.forecast_type)
        return strategy.generate(context)
