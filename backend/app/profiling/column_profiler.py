"""
Sentinel AI — Column Profiler

Generates comprehensive per-column statistics, completeness metrics, uniqueness ratios,
data distributions, text lengths, and date bounds.
"""

from typing import Any

import pandas as pd

from app.profiling.statistics_calculator import StatisticsCalculator


class ColumnProfiler:
    """Profiles individual DataFrame columns."""

    def __init__(self, calc: StatisticsCalculator | None = None) -> None:
        self.calc = calc or StatisticsCalculator()

    def profile_column(self, series: pd.Series, col_name: str, position: int) -> dict[str, Any]:
        """
        Generate a detailed statistical profile for a single pandas Series column.

        Returns:
            Dict containing general info, completeness, uniqueness, and type-specific metrics.
        """
        total_rows = len(series)
        null_count = int(series.isnull().sum())
        non_null_count = total_rows - null_count
        null_pct = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        non_null_pct = round(100.0 - null_pct, 2)

        unique_count = int(series.nunique(dropna=True))
        unique_pct = (
            round((unique_count / non_null_count) * 100, 2) if non_null_count > 0 else 0.0
        )
        duplicate_pct = round(100.0 - unique_pct, 2)

        memory_bytes = int(series.memory_usage(deep=True))
        pandas_dtype = str(series.dtype)

        # Base column profile structure
        profile: dict[str, Any] = {
            "column_name": col_name,
            "position": position,
            "pandas_dtype": pandas_dtype,
            "memory_bytes": memory_bytes,
            "completeness": {
                "null_count": null_count,
                "non_null_count": non_null_count,
                "null_percentage": null_pct,
                "non_null_percentage": non_null_pct,
            },
            "uniqueness": {
                "unique_count": unique_count,
                "unique_percentage": unique_pct,
                "duplicate_percentage": duplicate_pct,
            },
        }

        # Check column nature
        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_bool = pd.api.types.is_bool_dtype(series)
        is_datetime = pd.api.types.is_datetime64_any_dtype(series)

        if is_numeric and not is_bool:
            profile["type_category"] = "numeric"
            profile["statistics"] = self.calc.calculate_numeric_stats(series)
        elif is_datetime:
            profile["type_category"] = "datetime"
            profile["datetime_stats"] = self.calc.calculate_datetime_stats(series)
        elif is_bool:
            profile["type_category"] = "boolean"
            profile["categorical_stats"] = self.calc.calculate_categorical_stats(series)
        else:
            profile["type_category"] = "categorical"
            profile["categorical_stats"] = self.calc.calculate_categorical_stats(series)
            profile["text_stats"] = self.calc.calculate_text_stats(series)

        return profile
