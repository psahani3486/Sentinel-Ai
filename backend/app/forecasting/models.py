"""
Sentinel AI — Deterministic Mathematical Forecasting Models

Implements pluggable statistical forecasting models:
1. Simple Moving Average (SMA)
2. Weighted Moving Average (WMA)
3. Exponential Smoothing (EMA)
4. Linear Regression (Ordinary Least Squares)
"""

import abc
import math
from dataclasses import dataclass


@dataclass
class ForecastModelOutput:
    """Dataclass holding numerical prediction results from a statistical model."""

    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    slope: float = 0.0


class BaseForecastModel(abc.ABC):
    """Abstract interface for statistical forecasting models."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Model identifier name."""
        pass

    @abc.abstractmethod
    def predict(self, series: list[float], horizon_steps: int = 7) -> ForecastModelOutput:
        """
        Predict future values given a historical time series.

        Args:
            series: Historical float observation values.
            horizon_steps: Number of steps into the future.

        Returns:
            ForecastModelOutput with predicted value and confidence bounds.
        """
        pass


class SimpleMovingAverageModel(BaseForecastModel):
    """Simple Moving Average (SMA) model."""

    @property
    def name(self) -> str:
        return "SimpleMovingAverage"

    def predict(self, series: list[float], horizon_steps: int = 7) -> ForecastModelOutput:
        if not series:
            return ForecastModelOutput(0.0, 0.0, 0.0)
        window = series[-min(len(series), 5):]
        avg = sum(window) / len(window)
        # Compute standard deviation for confidence interval
        variance = sum((x - avg) ** 2 for x in window) / max(len(window), 1)
        std_dev = math.sqrt(variance)
        ci_margin = 1.96 * std_dev
        return ForecastModelOutput(
            predicted_value=round(avg, 2),
            confidence_interval_lower=round(avg - ci_margin, 2),
            confidence_interval_upper=round(avg + ci_margin, 2),
            slope=0.0,
        )


class WeightedMovingAverageModel(BaseForecastModel):
    """Weighted Moving Average (WMA) model giving higher weight to recent values."""

    @property
    def name(self) -> str:
        return "WeightedMovingAverage"

    def predict(self, series: list[float], horizon_steps: int = 7) -> ForecastModelOutput:
        if not series:
            return ForecastModelOutput(0.0, 0.0, 0.0)
        window = series[-min(len(series), 5):]
        weights = list(range(1, len(window) + 1))
        weighted_sum = sum(w * x for w, x in zip(weights, window, strict=False))
        wma = weighted_sum / sum(weights)
        variance = sum((x - wma) ** 2 for x in window) / max(len(window), 1)
        std_dev = math.sqrt(variance)
        ci_margin = 1.96 * std_dev
        return ForecastModelOutput(
            predicted_value=round(wma, 2),
            confidence_interval_lower=round(wma - ci_margin, 2),
            confidence_interval_upper=round(wma + ci_margin, 2),
            slope=0.0,
        )


class ExponentialSmoothingModel(BaseForecastModel):
    """Single Exponential Smoothing (EMA) model with alpha = 0.3."""

    def __init__(self, alpha: float = 0.3) -> None:
        self._alpha = alpha

    @property
    def name(self) -> str:
        return "ExponentialSmoothing"

    def predict(self, series: list[float], horizon_steps: int = 7) -> ForecastModelOutput:
        if not series:
            return ForecastModelOutput(0.0, 0.0, 0.0)
        s = series[0]
        for val in series[1:]:
            s = self._alpha * val + (1.0 - self._alpha) * s
        variance = sum((x - s) ** 2 for x in series) / max(len(series), 1)
        std_dev = math.sqrt(variance)
        ci_margin = 1.96 * std_dev
        return ForecastModelOutput(
            predicted_value=round(s, 2),
            confidence_interval_lower=round(s - ci_margin, 2),
            confidence_interval_upper=round(s + ci_margin, 2),
            slope=0.0,
        )


class LinearRegressionModel(BaseForecastModel):
    """Ordinary Least Squares Linear Regression model y = m * t + b."""

    @property
    def name(self) -> str:
        return "LinearRegression"

    def predict(self, series: list[float], horizon_steps: int = 7) -> ForecastModelOutput:
        n = len(series)
        if n < 2:
            val = series[0] if n == 1 else 0.0
            return ForecastModelOutput(val, val, val, 0.0)

        t = list(range(1, n + 1))
        sum_t = sum(t)
        sum_y = sum(series)
        sum_ty = sum(ti * yi for ti, yi in zip(t, series, strict=False))
        sum_t2 = sum(ti ** 2 for ti in t)

        denom = (n * sum_t2) - (sum_t ** 2)
        if abs(denom) < 1e-9:
            m = 0.0
            b = sum_y / n
        else:
            m = ((n * sum_ty) - (sum_t * sum_y)) / denom
            b = (sum_y - (m * sum_t)) / n

        t_future = n + horizon_steps
        pred = (m * t_future) + b

        # Compute standard error of the estimate
        residuals = [yi - ((m * ti) + b) for ti, yi in zip(t, series, strict=False)]
        sse = sum(r ** 2 for r in residuals)
        se = math.sqrt(sse / max(n - 2, 1))
        ci_margin = 1.96 * se

        return ForecastModelOutput(
            predicted_value=round(pred, 2),
            confidence_interval_lower=round(pred - ci_margin, 2),
            confidence_interval_upper=round(pred + ci_margin, 2),
            slope=round(m, 4),
        )
