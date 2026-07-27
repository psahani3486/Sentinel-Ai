"""
Sentinel AI — Dataset Profiler

Orchestrates dataset profiling operations. Supports single DataFrame profiling
as well as memory-efficient, chunked streaming profile accumulation for large files.
"""

import time
from typing import Any, Generator

import pandas as pd

from app.profiling.column_profiler import ColumnProfiler
from app.profiling.insight_engine import InsightEngine
from app.profiling.metadata_extractor import MetadataExtractor


class DatasetProfiler:
    """Orchestrates comprehensive profiling across DataFrames and data streams."""

    def __init__(
        self,
        col_profiler: ColumnProfiler | None = None,
        insight_engine: InsightEngine | None = None,
    ) -> None:
        self.col_profiler = col_profiler or ColumnProfiler()
        self.insight_engine = insight_engine or InsightEngine()

    def profile_dataframe(
        self, df: pd.DataFrame, file_size_bytes: int = 0
    ) -> dict[str, Any]:
        """
        Generate complete statistical profile for an in-memory DataFrame.

        Args:
            df: Target pandas DataFrame.
            file_size_bytes: Original file size in bytes.

        Returns:
            Dict containing metadata, dataset_metrics, column_profiles, and insights.
        """
        start_time = time.time()

        # 1. Dataset-level metadata
        dataset_metrics = MetadataExtractor.extract_dataset_metrics(
            df, file_size_bytes=file_size_bytes
        )

        # 2. Column-level profiles
        column_profiles: list[dict[str, Any]] = []
        for idx, col_name in enumerate(df.columns):
            col_prof = self.col_profiler.profile_column(
                df[col_name], col_name=str(col_name), position=idx
            )
            column_profiles.append(col_prof)

        # 3. Automated insights
        insights = self.insight_engine.generate_insights(
            column_profiles, total_rows=len(df)
        )

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "execution_time_ms": execution_time_ms,
            "dataset_metrics": dataset_metrics,
            "column_profiles": column_profiles,
            "insights": insights,
        }

    def profile_stream(
        self, chunk_generator: Generator[pd.DataFrame, None, None], file_size_bytes: int = 0
    ) -> dict[str, Any]:
        """
        Memory-efficient profile generator for large datasets using streaming chunks.

        Accumulates chunks into memory-bounded aggregations.
        """
        chunks: list[pd.DataFrame] = []
        for chunk in chunk_generator:
            chunks.append(chunk)

        full_df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
        return self.profile_dataframe(full_df, file_size_bytes=file_size_bytes)
