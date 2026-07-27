"""
Sentinel AI — Phase 2A Model Unit Tests

Verifies model creation, relationship integrity, column defaults, and enum constraints.
"""

import uuid
import pytest
from tests.conftest import TestSessionLocal

from app.models.dataset import (
    Dataset,
    DatasetColumn,
    DatasetProfile,
    DatasetSchema,
    DatasetVersion,
)
from app.models.enums import (
    ConnectorType,
    DatasetType,
    RuleType,
    RunStatus,
    ValidationSeverity,
    ValidationStatus,
)
from app.models.user import User, UserRole
from app.models.validation import (
    ValidationResult,
    ValidationRule,
    ValidationRun,
)


@pytest.mark.asyncio
async def test_dataset_and_version_models() -> None:
    """Verify Dataset and DatasetVersion entity creation and relationships."""
    async with TestSessionLocal() as session:
        user = User(
            email=f"owner-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Dataset Owner",
            role=UserRole.DATA_ENGINEER,
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(
            name="AI4I 2020 Predictive Maintenance",
            description="Smart factory machine sensor dataset",
            dataset_type=DatasetType.SENSOR_STREAM,
            connector_type=ConnectorType.INDUSTRIAL_SENSOR,
            connection_config={"sensor_frequency_hz": 10},
            owner_id=user.id,
        )
        session.add(dataset)
        await session.flush()

        assert dataset.id is not None
        assert dataset.is_active is True
        assert dataset.dataset_type == DatasetType.SENSOR_STREAM

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/data/storage/ai4i2020_v1.csv",
            row_count=10000,
            column_count=14,
            file_size_bytes=1048576,
            checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            ingested_by_id=user.id,
        )
        session.add(version)
        await session.flush()

        assert version.id is not None
        assert version.version_number == 1
        assert version.dataset_id == dataset.id


@pytest.mark.asyncio
async def test_schema_and_column_models() -> None:
    """Verify DatasetSchema and DatasetColumn creation and relationships."""
    async with TestSessionLocal() as session:
        user = User(
            email=f"schema-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Schema User",
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(
            name="NASA Turbofan Engine",
            dataset_type=DatasetType.TIME_SERIES,
            connector_type=ConnectorType.CSV,
            owner_id=user.id,
        )
        session.add(dataset)
        await session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/data/turbofan.csv",
            row_count=20000,
            column_count=26,
        )
        session.add(version)
        await session.flush()

        schema = DatasetSchema(
            dataset_version_id=version.id,
            column_count=2,
        )
        session.add(schema)
        await session.flush()

        col1 = DatasetColumn(
            dataset_schema_id=schema.id,
            column_name="unit_number",
            data_type="integer",
            is_nullable=False,
            is_primary_key=True,
            position=0,
            sample_values=[1, 2, 3],
        )
        col2 = DatasetColumn(
            dataset_schema_id=schema.id,
            column_name="time_cycles",
            data_type="integer",
            is_nullable=False,
            position=1,
            sample_values=[1, 2, 3, 4],
        )
        session.add_all([col1, col2])
        await session.flush()

        assert schema.id is not None
        assert col1.id is not None
        assert col1.is_primary_key is True
        assert col2.position == 1


@pytest.mark.asyncio
async def test_profile_and_validation_models() -> None:
    """Verify DatasetProfile, ValidationRule, ValidationRun, and ValidationResult."""
    async with TestSessionLocal() as session:
        user = User(
            email=f"val-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Validation User",
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(
            name="SECOM Dataset",
            dataset_type=DatasetType.TABULAR,
            connector_type=ConnectorType.CSV,
            owner_id=user.id,
        )
        session.add(dataset)
        await session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/data/secom.csv",
            row_count=1567,
            column_count=591,
        )
        session.add(version)
        await session.flush()

        profile = DatasetProfile(
            dataset_version_id=version.id,
            total_rows=1567,
            total_columns=591,
            memory_bytes=7400000,
            profile_data={"null_percentage": 4.5, "columns": {"sensor_1": {"mean": 12.4}}},
        )
        session.add(profile)

        rule = ValidationRule(
            name=f"Null Check {uuid.uuid4().hex[:6]}",
            rule_type=RuleType.MISSING_VALUES,
            severity=ValidationSeverity.HIGH,
            parameters={"max_null_pct": 5.0},
        )
        session.add(rule)
        await session.flush()

        run = ValidationRun(
            dataset_id=dataset.id,
            dataset_version_id=version.id,
            status=RunStatus.COMPLETED,
            overall_score=94.5,
            completeness_score=96.0,
            consistency_score=95.0,
            accuracy_score=93.0,
            freshness_score=100.0,
            execution_time_ms=145.2,
            triggered_by_id=user.id,
        )
        session.add(run)
        await session.flush()

        result = ValidationResult(
            validation_run_id=run.id,
            rule_id=rule.id,
            rule_type=RuleType.MISSING_VALUES,
            status=ValidationStatus.PASSED,
            severity=ValidationSeverity.HIGH,
            message="Missing values within acceptable SLA threshold",
            affected_columns=["sensor_1"],
            affected_rows_count=0,
            execution_time_ms=12.5,
            score_impact=0.0,
        )
        session.add(result)
        await session.flush()

        assert profile.id is not None
        assert rule.id is not None
        assert run.overall_score == 94.5
        assert result.status == ValidationStatus.PASSED
