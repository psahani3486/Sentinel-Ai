"""
Sentinel AI — Metadata Extractor

Extracts dataset-level metrics including row counts, column counts, memory usage,
missing cell counts, duplicate row counts, density, and sparsity.
"""

from typing import Any

import pandas as pd


class MetadataExtractor:
    """Extracts overall dataset-level properties and memory metrics."""

    @staticmethod
    def extract_dataset_metrics(
        df: pd.DataFrame, file_size_bytes: int = 0
    ) -> dict[str, Any]:
        """
        Extract high-level metrics for a pandas DataFrame.

        Args:
            df: Target DataFrame.
            file_size_bytes: Original file size in bytes if applicable.

        Returns:
            Dict containing row_count, column_count, memory_bytes, duplicate_rows,
            missing_cells, dataset_density_pct, dataset_sparsity_pct.
        """
        row_count = len(df)
        col_count = len(df.columns)
        total_cells = row_count * col_count

        memory_bytes = int(df.memory_usage(deep=True).sum())
        duplicate_rows = int(df.duplicated().sum())
        missing_cells = int(df.isnull().sum().sum())

        density_pct = (
            round(((total_cells - missing_cells) / total_cells) * 100, 2)
            if total_cells > 0
            else 100.0
        )
        sparsity_pct = round(100.0 - density_pct, 2)

        return {
            "row_count": row_count,
            "column_count": col_count,
            "total_cells": total_cells,
            "file_size_bytes": file_size_bytes,
            "memory_bytes": memory_bytes,
            "duplicate_rows_count": duplicate_rows,
            "duplicate_rows_pct": (
                round((duplicate_rows / row_count) * 100, 2) if row_count > 0 else 0.0
            ),
            "missing_cells_count": missing_cells,
            "missing_cells_pct": (
                round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
            ),
            "dataset_density_pct": density_pct,
            "dataset_sparsity_pct": sparsity_pct,
        }
