"""
Sentinel AI — Statistics Calculator

High-precision statistical calculation helper operating on pandas Series and NumPy arrays.
Computes numeric summary statistics, quantiles, percentiles, skewness, kurtosis,
text length distributions, date ranges, and categorical entropy/frequencies.
"""

import math
from typing import Any

import numpy as np
import pandas as pd


class StatisticsCalculator:
    """Statistical calculation engine for dataset column profiling."""

    @staticmethod
    def calculate_numeric_stats(series: pd.Series) -> dict[str, Any]:
        """
        Compute numeric summary statistics for a numeric column.

        Returns:
            Dict containing min, max, mean, median, mode, std, variance, sum, range,
            skewness, kurtosis, and percentiles (P1, P5, P25, P50, P75, P95, P99).
        """
        clean_series = series.dropna()

        if clean_series.empty:
            return {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "mode": None,
                "std": None,
                "variance": None,
                "sum": None,
                "range": None,
                "skewness": None,
                "kurtosis": None,
                "percentiles": {},
            }

        # Convert to float NumPy array for numerical stability
        arr = clean_series.to_numpy(dtype=float)

        min_val = float(np.min(arr))
        max_val = float(np.max(arr))
        mean_val = float(np.mean(arr))
        median_val = float(np.median(arr))
        std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        var_val = float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0
        sum_val = float(np.sum(arr))
        range_val = max_val - min_val

        # Mode calculation
        mode_series = clean_series.mode()
        mode_val = float(mode_series.iloc[0]) if not mode_series.empty else None

        # Skewness and Kurtosis
        skew_val = float(clean_series.skew()) if len(arr) > 2 else 0.0
        kurt_val = float(clean_series.kurtosis()) if len(arr) > 3 else 0.0

        # Replace NaN / Inf values
        skew_val = 0.0 if (math.isnan(skew_val) or math.isinf(skew_val)) else skew_val
        kurt_val = 0.0 if (math.isnan(kurt_val) or math.isinf(kurt_val)) else kurt_val

        # Percentiles
        percentile_levels = [1, 5, 25, 50, 75, 95, 99]
        percentile_vals = np.percentile(arr, percentile_levels)
        percentiles = {
            f"p{p}": float(v) for p, v in zip(percentile_levels, percentile_vals)
        }

        return {
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
            "median": median_val,
            "mode": mode_val,
            "std": std_val,
            "variance": var_val,
            "sum": sum_val,
            "range": range_val,
            "skewness": skew_val,
            "kurtosis": kurt_val,
            "quartiles": {
                "q1": percentiles["p25"],
                "q2": percentiles["p50"],
                "q3": percentiles["p75"],
                "iqr": percentiles["p75"] - percentiles["p25"],
            },
            "percentiles": percentiles,
        }

    @staticmethod
    def calculate_categorical_stats(series: pd.Series, top_k: int = 10) -> dict[str, Any]:
        """
        Compute top value frequencies, ratios, and Shannon Entropy for categorical columns.
        """
        clean_series = series.dropna().astype(str)

        if clean_series.empty:
            return {
                "top_values": [],
                "entropy": 0.0,
            }

        total_count = len(clean_series)
        value_counts = clean_series.value_counts()
        top_counts = value_counts.head(top_k)

        top_values = [
            {
                "value": str(val),
                "count": int(cnt),
                "percentage": round((cnt / total_count) * 100, 2),
            }
            for val, cnt in top_counts.items()
        ]

        # Calculate Shannon Entropy: H(X) = -sum(p(x) * log2(p(x)))
        probs = value_counts.to_numpy() / total_count
        entropy_val = float(-np.sum(probs * np.log2(probs + 1e-12)))

        return {
            "top_values": top_values,
            "entropy": round(entropy_val, 4),
        }

    @staticmethod
    def calculate_text_stats(series: pd.Series) -> dict[str, Any]:
        """Compute string length statistics (min, max, average length)."""
        clean_series = series.dropna().astype(str)

        if clean_series.empty:
            return {
                "min_length": 0,
                "max_length": 0,
                "avg_length": 0.0,
            }

        lengths = clean_series.str.len()
        return {
            "min_length": int(lengths.min()),
            "max_length": int(lengths.max()),
            "avg_length": round(float(lengths.mean()), 2),
        }

    @staticmethod
    def calculate_datetime_stats(series: pd.Series) -> dict[str, Any]:
        """Compute date bounds and time span for date/time columns."""
        dt_series = pd.to_datetime(series, errors="coerce").dropna()

        if dt_series.empty:
            return {
                "earliest_date": None,
                "latest_date": None,
                "time_span_days": 0.0,
            }

        earliest = dt_series.min()
        latest = dt_series.max()
        span_days = (latest - earliest).total_seconds() / 86400.0

        return {
            "earliest_date": earliest.isoformat(),
            "latest_date": latest.isoformat(),
            "time_span_days": round(span_days, 2),
        }
