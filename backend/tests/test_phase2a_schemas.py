"""
Sentinel AI — Phase 2A Pydantic Schema Unit Tests

Verifies Pydantic v2 schema validations and serialization for Phase 2A DTOs.
"""

import uuid
import pytest
from pydantic import ValidationError

from app.models.enums import ConnectorType, DatasetType, RuleType, ValidationSeverity
from app.schemas.dataset import (
    DatasetColumnCreate,
    DatasetCreate,
    DatasetUpdate,
    DatasetVersionCreate,
)
from app.schemas.validation import (
    ValidationResultCreate,
    ValidationRuleCreate,
    ValidationRunCreate,
)


def test_dataset_schema_validations() -> None:
    """Verify DatasetCreate and DatasetUpdate validation constraints."""
    ds_create = DatasetCreate(
        name="Predictive Maintenance AI4I",
        description="Dataset for failure prediction",
        dataset_type=DatasetType.SENSOR_STREAM,
        connector_type=ConnectorType.INDUSTRIAL_SENSOR,
    )
    assert ds_create.name == "Predictive Maintenance AI4I"

    # Test short name failure
    with pytest.raises(ValidationError):
        DatasetCreate(name="A")

    ds_update = DatasetUpdate(name="Updated Name", is_active=False)
    assert ds_update.name == "Updated Name"
    assert ds_update.is_active is False


def test_version_and_column_schema_validations() -> None:
    """Verify DatasetVersionCreate and DatasetColumnCreate validation rules."""
    ver_create = DatasetVersionCreate(
        storage_path="/data/storage/version_1.csv",
        row_count=1500,
        column_count=20,
        file_size_bytes=450000,
    )
    assert ver_create.row_count == 1500

    col_create = DatasetColumnCreate(
        column_name="air_temperature",
        data_type="float",
        position=0,
        is_nullable=False,
    )
    assert col_create.column_name == "air_temperature"


def test_validation_rule_and_result_schemas() -> None:
    """Verify ValidationRuleCreate and ValidationResultCreate models."""
    rule_create = ValidationRuleCreate(
        name="Temperature Range Rule",
        rule_type=RuleType.INVALID_SENSOR_RANGE,
        severity=ValidationSeverity.HIGH,
        parameters={"min": 250.0, "max": 350.0},
    )
    assert rule_create.severity == ValidationSeverity.HIGH

    run_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    run_create = ValidationRunCreate(
        dataset_id=run_id,
        dataset_version_id=ver_id,
    )
    assert run_create.dataset_id == run_id

    res_create = ValidationResultCreate(
        rule_type=RuleType.INVALID_SENSOR_RANGE,
        status="failed",
        severity=ValidationSeverity.HIGH,
        message="5 readings out of bounds",
        affected_columns=["air_temperature"],
        affected_rows_count=5,
    )
    assert res_create.affected_rows_count == 5
