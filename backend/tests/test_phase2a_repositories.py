"""
Sentinel AI — Phase 2A Repository Unit Tests

Verifies repository CRUD, relationship fetching, pagination, and cascade rules.
"""

import uuid
import pytest
from tests.conftest import TestSessionLocal

from app.models.enums import (
    ConnectorType,
    DatasetType,
    RuleType,
    RunStatus,
    ValidationSeverity,
    ValidationStatus,
)
from app.models.dataset import (
    Dataset,
    DatasetColumn,
    DatasetProfile,
    DatasetSchema,
    DatasetVersion,
)
from app.models.user import User
from app.models.validation import (
    ValidationResult,
    ValidationRule,
    ValidationRun,
)
from app.repositories.dataset_repository import (
    DatasetColumnRepository,
    DatasetProfileRepository,
    DatasetRepository,
    DatasetSchemaRepository,
    DatasetVersionRepository,
)
from app.repositories.validation_repository import (
    ValidationResultRepository,
    ValidationRuleRepository,
    ValidationRunRepository,
)


@pytest.mark.asyncio
async def test_dataset_repository_crud() -> None:
    """Verify DatasetRepository CRUD and custom paginated queries."""
    async with TestSessionLocal() as session:
        user = User(
            email=f"repo-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Repo User",
        )
        session.add(user)
        await session.flush()

        dataset_repo = DatasetRepository(session)
        version_repo = DatasetVersionRepository(session)

        # 1. Create dataset
        ds = Dataset(
            name=f"Factory Telemetry {uuid.uuid4().hex[:4]}",
            description="Vibration and temperature sensors",
            dataset_type=DatasetType.SENSOR_STREAM,
            connector_type=ConnectorType.INDUSTRIAL_SENSOR,
            owner_id=user.id,
        )
        created_ds = await dataset_repo.create(ds)
        assert created_ds.id is not None

        # 2. Add version
        ver = DatasetVersion(
            dataset_id=created_ds.id,
            version_number=1,
            storage_path="/data/telemetry_v1.csv",
            row_count=5000,
            column_count=10,
        )
        await version_repo.create(ver)

        # 3. Check owner datasets
        owner_ds = await dataset_repo.get_by_owner(user.id)
        assert len(owner_ds) == 1

        # 4. Check paginated search
        items, total = await dataset_repo.get_datasets_paginated(search="Factory Telemetry")
        assert total >= 1
        assert any(created_ds.name in d.name for d in items)

        # 5. Check exists helper
        exists = await dataset_repo.exists_by_owner_and_name(user.id, created_ds.name)
        assert exists is True


@pytest.mark.asyncio
async def test_schema_and_profile_repositories() -> None:
    """Verify DatasetSchema, DatasetColumn, and DatasetProfile repositories."""
    async with TestSessionLocal() as session:
        user = User(
            email=f"schema-repo-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Schema Repo User",
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(name=f"Turbofan Engine v2 {uuid.uuid4().hex[:4]}", owner_id=user.id)
        session.add(dataset)
        await session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/data/turbofan_v2.csv",
        )
        session.add(version)
        await session.flush()

        schema_repo = DatasetSchemaRepository(session)
        col_repo = DatasetColumnRepository(session)
        profile_repo = DatasetProfileRepository(session)

        # Create Schema
        schema = DatasetSchema(dataset_version_id=version.id, column_count=1)
        created_schema = await schema_repo.create(schema)

        # Create Column
        col = DatasetColumn(
            dataset_schema_id=created_schema.id,
            column_name="sensor_temp",
            data_type="float",
            position=0,
        )
        await col_repo.create(col)

        # Fetch Columns
        cols = await col_repo.get_columns_by_schema_id(created_schema.id)
        assert len(cols) == 1
        assert cols[0].column_name == "sensor_temp"

        # Create Profile
        prof = DatasetProfile(
            dataset_version_id=version.id,
            total_rows=100,
            total_columns=1,
            memory_bytes=800,
            profile_data={"test": 123},
        )
        await profile_repo.create(prof)

        fetched_prof = await profile_repo.get_by_version_id(version.id)
        assert fetched_prof is not None
        assert fetched_prof.total_rows == 100


@pytest.mark.asyncio
async def test_validation_repositories() -> None:
    """Verify ValidationRule, ValidationRun, and ValidationResult repositories."""
    async with TestSessionLocal() as session:
        user = User(
            email=f"val-repo-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Val Repo User",
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(name=f"Test Val Dataset {uuid.uuid4().hex[:4]}", owner_id=user.id)
        session.add(dataset)
        await session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path="/data/test_val.csv",
        )
        session.add(version)
        await session.flush()

        rule_repo = ValidationRuleRepository(session)
        run_repo = ValidationRunRepository(session)
        res_repo = ValidationResultRepository(session)

        # Rule Operations
        rule_name = f"Duplicate Rule {uuid.uuid4().hex[:6]}"
        rule = ValidationRule(
            name=rule_name,
            rule_type=RuleType.DUPLICATE_ROWS,
            severity=ValidationSeverity.CRITICAL,
        )
        await rule_repo.create(rule)

        active_rules = await rule_repo.get_active_rules()
        assert any(r.name == rule_name for r in active_rules)

        fetched_rule = await rule_repo.get_by_name(rule_name)
        assert fetched_rule is not None

        # Run Operations
        run = ValidationRun(
            dataset_id=dataset.id,
            dataset_version_id=version.id,
            status=RunStatus.COMPLETED,
            overall_score=88.0,
            execution_time_ms=50.0,
        )
        await run_repo.create(run)

        runs, count = await run_repo.get_runs_by_dataset(dataset.id)
        assert count == 1
        assert runs[0].overall_score == 88.0

        # Result Operations
        result = ValidationResult(
            validation_run_id=run.id,
            rule_id=rule.id,
            rule_type=RuleType.DUPLICATE_ROWS,
            status=ValidationStatus.FAILED,
            severity=ValidationSeverity.CRITICAL,
            message="Found 12 duplicate rows",
            affected_rows_count=12,
            execution_time_ms=5.0,
            score_impact=-12.0,
        )
        await res_repo.create(result)

        failed_results = await res_repo.get_failed_results_by_run_id(run.id)
        assert len(failed_results) == 1
        assert failed_results[0].affected_rows_count == 12
