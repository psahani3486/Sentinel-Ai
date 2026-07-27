"""
Sentinel AI — Phase 2C Profiling Engine Unit & Integration Tests

Verifies StatisticsCalculator accuracy, MetadataExtractor formulas, ColumnProfiler metrics,
InsightEngine rule checks, DatasetProfiler streaming, and ProfilingService persistence & diffing.
"""

import os
import uuid
import numpy as np
import pandas as pd
import pytest

from app.models.dataset import Dataset, DatasetVersion
from app.models.enums import ConnectorType
from app.models.user import User
from app.profiling.column_profiler import ColumnProfiler
from app.profiling.dataset_profiler import DatasetProfiler
from app.profiling.insight_engine import InsightEngine
from app.profiling.metadata_extractor import MetadataExtractor
from app.profiling.statistics_calculator import StatisticsCalculator
from app.repositories.dataset_repository import DatasetProfileRepository
from app.services.profiling_service import ProfilingService
from tests.conftest import TestSessionLocal


@pytest.fixture
def sample_ai4i_file() -> str:
    """Return path to sample AI4I 2020 dataset file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", "ai4i2020.csv")


# ── 1. StatisticsCalculator Unit Tests ────────────────────────────────────────

def test_statistics_calculator_numeric() -> None:
    """Verify numeric statistical calculations and percentile accuracy."""
    series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, np.nan])
    stats = StatisticsCalculator.calculate_numeric_stats(series)

    assert stats["min"] == 10.0
    assert stats["max"] == 50.0
    assert stats["mean"] == 30.0
    assert stats["median"] == 30.0
    assert stats["sum"] == 150.0
    assert stats["range"] == 40.0
    assert stats["percentiles"]["p50"] == 30.0
    assert stats["quartiles"]["iqr"] == 20.0


def test_statistics_calculator_categorical_and_text() -> None:
    """Verify categorical top frequencies, entropy, and text length stats."""
    cat_series = pd.Series(["A", "A", "B", "C", "A", np.nan])
    cat_stats = StatisticsCalculator.calculate_categorical_stats(cat_series, top_k=2)

    assert len(cat_stats["top_values"]) == 2
    assert cat_stats["top_values"][0]["value"] == "A"
    assert cat_stats["top_values"][0]["count"] == 3
    assert cat_stats["entropy"] > 0.0

    text_series = pd.Series(["hello", "world!", "a"])
    text_stats = StatisticsCalculator.calculate_text_stats(text_series)
    assert text_stats["min_length"] == 1
    assert text_stats["max_length"] == 6
    assert text_stats["avg_length"] == 4.0


def test_statistics_calculator_datetime() -> None:
    """Verify date bounds and time span calculation."""
    dt_series = pd.Series(["2026-01-01", "2026-01-11", None])
    dt_stats = StatisticsCalculator.calculate_datetime_stats(dt_series)

    assert dt_stats["earliest_date"].startswith("2026-01-01")
    assert dt_stats["latest_date"].startswith("2026-01-11")
    assert dt_stats["time_span_days"] == 10.0


# ── 2. MetadataExtractor & ColumnProfiler Unit Tests ─────────────────────────

def test_metadata_extractor() -> None:
    """Verify MetadataExtractor dataset density, sparsity, and memory formulas."""
    df = pd.DataFrame({
        "a": [1, 2, None, 4],
        "b": ["x", "y", "z", "w"],
    })
    metrics = MetadataExtractor.extract_dataset_metrics(df, file_size_bytes=100)

    assert metrics["row_count"] == 4
    assert metrics["column_count"] == 2
    assert metrics["total_cells"] == 8
    assert metrics["missing_cells_count"] == 1
    assert metrics["dataset_density_pct"] == 87.5
    assert metrics["dataset_sparsity_pct"] == 12.5


def test_column_profiler() -> None:
    """Verify ColumnProfiler profile generation."""
    profiler = ColumnProfiler()
    series = pd.Series([10, 20, 30, 40, 50], name="speed")

    prof = profiler.profile_column(series, col_name="speed", position=0)
    assert prof["column_name"] == "speed"
    assert prof["type_category"] == "numeric"
    assert prof["completeness"]["null_count"] == 0
    assert prof["uniqueness"]["unique_count"] == 5


# ── 3. InsightEngine Unit Tests ───────────────────────────────────────────────

def test_insight_engine() -> None:
    """Verify InsightEngine anomaly detection rules and candidate flags."""
    profiles = [
        {
            "column_name": "id",
            "completeness": {"null_count": 0, "null_percentage": 0.0},
            "uniqueness": {"unique_count": 100, "unique_percentage": 100.0},
            "type_category": "numeric",
            "statistics": {"skewness": 0.1},
        },
        {
            "column_name": "constant_sensor",
            "completeness": {"null_count": 0, "null_percentage": 0.0},
            "uniqueness": {"unique_count": 1, "unique_percentage": 1.0},
            "type_category": "numeric",
            "statistics": {"skewness": 0.0},
        },
        {
            "column_name": "missing_sensor",
            "completeness": {"null_count": 30, "null_percentage": 30.0},
            "uniqueness": {"unique_count": 50, "unique_percentage": 50.0},
            "type_category": "numeric",
            "statistics": {"skewness": 2.5},  # highly skewed
        },
        {
            "column_name": "machine_failure",
            "completeness": {"null_count": 0, "null_percentage": 0.0},
            "uniqueness": {"unique_count": 2, "unique_percentage": 2.0},
            "type_category": "numeric",
            "statistics": {"skewness": 0.0},
        },
        {
            "column_name": "recorded_timestamp",
            "completeness": {"null_count": 0, "null_percentage": 0.0},
            "uniqueness": {"unique_count": 100, "unique_percentage": 100.0},
            "type_category": "datetime",
        },
    ]

    insights = InsightEngine.generate_insights(profiles, total_rows=100)

    assert "constant_sensor" in insights["constant_columns"]
    assert "id" in insights["candidate_primary_keys"]
    assert any(c["column_name"] == "missing_sensor" for c in insights["high_missing_value_columns"])
    assert any(c["column_name"] == "missing_sensor" for c in insights["highly_skewed_columns"])
    assert "recorded_timestamp" in insights["timestamp_candidates"]
    assert "machine_failure" in insights["possible_target_columns"]
    assert len(insights["actionable_warnings"]) >= 2


# ── 4. DatasetProfiler Unit Tests ─────────────────────────────────────────────

def test_dataset_profiler_dataframe() -> None:
    """Verify DatasetProfiler dataframe and chunk streaming profiling."""
    profiler = DatasetProfiler()
    df = pd.DataFrame({
        "temp": [300.0, 301.2, 302.5, 304.1],
        "status": ["OK", "OK", "FAIL", "OK"],
    })

    prof = profiler.profile_dataframe(df, file_size_bytes=500)
    assert prof["dataset_metrics"]["row_count"] == 4
    assert len(prof["column_profiles"]) == 2
    assert "insights" in prof

    # Stream profiling test
    def chunk_gen():
        yield df.iloc[:2]
        yield df.iloc[2:]

    stream_prof = profiler.profile_stream(chunk_gen(), file_size_bytes=500)
    assert stream_prof["dataset_metrics"]["row_count"] == 4


# ── 5. ProfilingService & Persistence Integration Tests ─────────────────────

@pytest.mark.asyncio
async def test_profiling_service_generate_and_persist(sample_ai4i_file: str) -> None:
    """Verify ProfilingService profile generation, database persistence, and profile diffing."""
    config = {"file_path": sample_ai4i_file}

    async with TestSessionLocal() as session:
        user = User(
            email=f"prof-user-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Profiling User",
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(name="Profiling AI4I", owner_id=user.id)
        session.add(dataset)
        await session.flush()

        version_v1 = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path=sample_ai4i_file,
        )
        session.add(version_v1)
        await session.flush()

        version_v2 = DatasetVersion(
            dataset_id=dataset.id,
            version_number=2,
            storage_path=sample_ai4i_file,
        )
        session.add(version_v2)
        await session.flush()

        profile_repo = DatasetProfileRepository(session)
        prof_service = ProfilingService(profile_repository=profile_repo)

        # 1. Profile and Persist Version 1
        db_prof_v1 = await prof_service.profile_and_persist(
            version_v1.id, ConnectorType.CSV, config
        )
        assert db_prof_v1.id is not None
        assert db_prof_v1.total_rows == 16
        assert db_prof_v1.total_columns == 14

        # 2. Profile and Persist Version 2
        db_prof_v2 = await prof_service.profile_and_persist(
            version_v2.id, ConnectorType.INDUSTRIAL_SENSOR, config
        )
        assert db_prof_v2.id is not None

        # 3. Compare Version 1 and Version 2 Profiles
        diff = prof_service.compare_profiles(
            db_prof_v1.profile_data, db_prof_v2.profile_data
        )
        assert diff["row_count_diff"] == 0
        assert diff["added_columns"] == []
        assert diff["removed_columns"] == []
