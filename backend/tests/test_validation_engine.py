"""
Sentinel AI — Phase 2D Enterprise Validation Engine Unit & Integration Tests

Tests all 22 validation rules, RuleRegistry dynamic creation, RuleExecutor isolation,
ScoreCalculator weighted penalties, ValidationReporter historical comparisons,
ValidationEngine execution, and ValidationService database persistence.
"""

import os
import uuid
import numpy as np
import pandas as pd
import pytest

from app.models.dataset import Dataset, DatasetVersion
from app.models.enums import ConnectorType, RuleType, RunStatus, ValidationSeverity, ValidationStatus
from app.models.user import User
from app.repositories.validation_repository import (
    ValidationResultRepository,
    ValidationRunRepository,
)
from app.services.validation_service import ValidationService
from app.validation_engine.base_rule import RuleCategory, RuleResult
from app.validation_engine.engine import ValidationEngine
from app.validation_engine.executor import RuleExecutor
from app.validation_engine.registry import RuleRegistry
from app.validation_engine.reporter import ValidationReporter
from app.validation_engine.rules import (
    ColumnStatisticsRule,
    ConstantColumnRule,
    CrossColumnBusinessRule,
    DataAccuracyRule,
    DataCompletenessRule,
    DataConsistencyRule,
    DuplicateColumnRule,
    DuplicateRowsRule,
    FreshnessRule,
    HighCardinalityRule,
    InvalidNumericRule,
    InvalidTimestampRule,
    LowCardinalityRule,
    MissingValuesRule,
    NegativeSensorValueRule,
    NullColumnRule,
    OutlierRule,
    PrimaryKeyRule,
    SchemaChangeRule,
    SensorRangeRule,
    UniqueConstraintRule,
    WrongDataTypeRule,
)
from app.validation_engine.score_calculator import ScoreCalculator
from tests.conftest import TestSessionLocal


@pytest.fixture
def sample_ai4i_file() -> str:
    """Return path to sample AI4I 2020 dataset file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", "ai4i2020.csv")


# ── 1. RuleRegistry & RuleExecutor Unit Tests ─────────────────────────────────

def test_rule_registry() -> None:
    """Verify RuleRegistry registration, lookup, list, and category filtering."""
    supported = RuleRegistry.list_supported_rules()
    assert len(supported) == 22
    assert "missing_values" in supported
    assert "invalid_sensor_range" in supported

    rule_inst = RuleRegistry.create(RuleType.MISSING_VALUES, config={"max_null_percentage": 2.0})
    assert isinstance(rule_inst, MissingValuesRule)
    assert rule_inst.config["max_null_percentage"] == 2.0

    comp_rules = RuleRegistry.get_rules_by_category(RuleCategory.COMPLETENESS)
    assert len(comp_rules) >= 3


def test_rule_executor_error_handling() -> None:
    """Verify RuleExecutor catches exceptions and converts to RuleResult ERROR."""
    class BrokenRule(MissingValuesRule):
        def validate(self, df, schema_info=None, history=None):
            raise ValueError("Simulated catastrophic rule failure")

    rule = BrokenRule()
    df = pd.DataFrame({"a": [1, 2, 3]})
    res = RuleExecutor.execute_rule(rule, df)

    assert res.status == ValidationStatus.ERROR
    assert "Simulated catastrophic rule failure" in res.message


# ── 2. The 22 Validation Rules Unit Tests ─────────────────────────────────────

def test_completeness_rules() -> None:
    """Test MissingValuesRule, NullColumnRule, DataCompletenessRule."""
    df = pd.DataFrame({
        "good": [1, 2, 3, 4],
        "part_null": [1, None, None, 4],
        "all_null": [None, None, None, None],
    })

    # MissingValuesRule
    r1 = MissingValuesRule({"max_null_percentage": 10.0})
    res1 = r1.validate(df)
    assert res1.status == ValidationStatus.FAILED
    assert "part_null" in res1.affected_columns or "all_null" in res1.affected_columns

    # NullColumnRule
    r2 = NullColumnRule()
    res2 = r2.validate(df)
    assert res2.status == ValidationStatus.FAILED
    assert "all_null" in res2.affected_columns

    # DataCompletenessRule
    r3 = DataCompletenessRule({"min_completeness_pct": 90.0})
    res3 = r3.validate(df)
    assert res3.status == ValidationStatus.FAILED


def test_consistency_rules() -> None:
    """Test DuplicateRowsRule, DuplicateColumnRule, DataConsistencyRule."""
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "air": [300.0, 300.0, 290.0],
        "proc": [290.0, 290.0, 310.0],  # row 0 & 1 fail proc >= air constraint
    })

    r1 = DuplicateRowsRule({"max_duplicate_percentage": 0.0})
    res1 = r1.validate(df)
    assert res1.status == ValidationStatus.FAILED

    r2 = DuplicateColumnRule()
    res2 = r2.validate(df)
    assert res2.status == ValidationStatus.PASSED

    r3 = DataConsistencyRule({"expression": "`proc` >= `air`"})
    res3 = r3.validate(df)
    assert res3.status == ValidationStatus.FAILED
    assert res3.affected_rows_count == 2


def test_accuracy_rules() -> None:
    """Test InvalidNumericRule, NegativeSensorValueRule, SensorRangeRule, DataAccuracyRule."""
    df = pd.DataFrame({
        "temperature": [300.0, np.nan, 290.0, 280.0],
        "rotational_speed": [-100.0, 1500.0, 1600.0, 1400.0],
        "sensor_deadlocked": [50.0, 50.0, 50.0, 50.0],
    })

    r1 = InvalidNumericRule()
    res1 = r1.validate(df)
    assert res1.status == ValidationStatus.FAILED

    r2 = NegativeSensorValueRule({"columns": ["rotational_speed"]})
    res2 = r2.validate(df)
    assert res2.status == ValidationStatus.FAILED
    assert "rotational_speed" in res2.affected_columns

    r3 = SensorRangeRule({"ranges": {"rotational_speed": {"min": 0.0, "max": 2000.0}}})
    res3 = r3.validate(df)
    assert res3.status == ValidationStatus.FAILED

    r4 = DataAccuracyRule()
    res4 = r4.validate(df)
    assert res4.status == ValidationStatus.FAILED
    assert "sensor_deadlocked" in res4.affected_columns


def test_freshness_rules() -> None:
    """Test InvalidTimestampRule, FreshnessRule."""
    df = pd.DataFrame({
        "timestamp": ["2026-01-01 10:00:00", "invalid_date_str", "2026-01-02 12:00:00"],
    })

    r1 = InvalidTimestampRule()
    res1 = r1.validate(df)
    assert res1.status == ValidationStatus.FAILED

    r2 = FreshnessRule({"max_lag_hours": 24.0})
    res2 = r2.validate(df)
    assert res2.status == ValidationStatus.PASSED


def test_schema_rules() -> None:
    """Test WrongDataTypeRule, SchemaChangeRule, PrimaryKeyRule, UniqueConstraintRule."""
    df = pd.DataFrame({
        "udi": [1, 2, 2],  # Duplicate PK
        "type": ["L", "M", "H"],
    })

    r1 = WrongDataTypeRule({"expected_types": {"udi": "float"}})
    res1 = r1.validate(df)
    assert res1.status == ValidationStatus.PASSED

    r2 = SchemaChangeRule({"expected_columns": ["udi", "type", "missing_col"]})
    res2 = r2.validate(df)
    assert res2.status == ValidationStatus.FAILED

    r3 = PrimaryKeyRule({"columns": ["udi"]})
    res3 = r3.validate(df)
    assert res3.status == ValidationStatus.FAILED

    r4 = UniqueConstraintRule({"columns": ["udi"]})
    res4 = r4.validate(df)
    assert res4.status == ValidationStatus.FAILED


def test_statistical_and_business_rules() -> None:
    """Test OutlierRule, ConstantColumnRule, HighCardinalityRule, LowCardinalityRule, ColumnStatisticsRule, CrossColumnBusinessRule."""
    df = pd.DataFrame({
        "val": [10.0, 10.1, 10.2, 10.0, 1000.0],  # Outlier 1000.0
        "const": [5.0, 5.0, 5.0, 5.0, 5.0],
        "cat": ["A", "B", "C", "D", "E"],
    })

    r1 = OutlierRule({"z_threshold": 1.5})
    res1 = r1.validate(df)
    assert res1.status == ValidationStatus.WARNING

    r2 = ConstantColumnRule()
    res2 = r2.validate(df)
    assert res2.status == ValidationStatus.WARNING
    assert "const" in res2.affected_columns

    r3 = HighCardinalityRule({"max_unique_pct": 50.0})
    res3 = r3.validate(df)
    assert res3.status in (ValidationStatus.PASSED, ValidationStatus.WARNING)

    r4 = LowCardinalityRule({"min_unique_count": 3})
    res4 = r4.validate(df)
    assert res4.status in (ValidationStatus.PASSED, ValidationStatus.WARNING)

    r5 = ColumnStatisticsRule({"stat_bounds": {"val": {"min_mean": 0.0, "max_mean": 50.0}}})
    res5 = r5.validate(df)
    assert res5.status == ValidationStatus.FAILED

    r6 = CrossColumnBusinessRule({"business_query": "val < 100.0"})
    res6 = r6.validate(df)
    assert res6.status == ValidationStatus.FAILED


# ── 3. ScoreCalculator & ValidationReporter Unit Tests ──────────────────────

def test_score_calculator() -> None:
    """Verify ScoreCalculator weighted scoring formulas and severity deductions."""
    calc = ScoreCalculator()
    results = [
        RuleResult(
            rule_name="Pass Rule",
            rule_type=RuleType.MISSING_VALUES,
            category=RuleCategory.COMPLETENESS,
            status=ValidationStatus.PASSED,
            severity=ValidationSeverity.HIGH,
            message="OK",
        ),
        RuleResult(
            rule_name="Fail Rule",
            rule_type=RuleType.NEGATIVE_SENSOR_VALUES,
            category=RuleCategory.ACCURACY,
            status=ValidationStatus.FAILED,
            severity=ValidationSeverity.HIGH,  # -15 penalty
            message="Fail",
        ),
    ]

    scores = calc.calculate_scores(results)
    assert scores["category_scores"]["completeness"] == 100.0
    assert scores["category_scores"]["accuracy"] == 85.0
    assert scores["overall_score"] < 100.0


def test_validation_reporter_history() -> None:
    """Verify ValidationReporter historical trend comparison."""
    current_results = [
        RuleResult(
            rule_name="Missing Values Rule",
            rule_type=RuleType.MISSING_VALUES,
            category=RuleCategory.COMPLETENESS,
            status=ValidationStatus.PASSED,
            severity=ValidationSeverity.HIGH,
            message="Resolved",
        )
    ]
    history = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "summary": {"overall_score": 75.0},
            "failed_rules": [{"rule_name": "Missing Values Rule", "status": "FAILED"}],
        }
    ]

    report = ValidationReporter.generate_report(current_results, {"overall_score": 100.0}, 10.0, history=history)
    hist_comp = report["historical_comparison"]

    assert hist_comp["has_previous_run"] is True
    assert "Missing Values Rule" in hist_comp["improvements"]
    assert hist_comp["status"] == "IMPROVED"


# ── 4. ValidationEngine & ValidationService Integration Tests ───────────────

def test_validation_engine(sample_ai4i_file: str) -> None:
    """Verify ValidationEngine execution on AI4I sample dataset."""
    engine = ValidationEngine()
    df = pd.read_csv(sample_ai4i_file)

    report = engine.run_validations(df)
    assert "summary" in report
    assert report["summary"]["total_rules_executed"] == 22
    assert report["summary"]["overall_score"] > 0.0


@pytest.mark.asyncio
async def test_validation_service_run_and_persist(sample_ai4i_file: str) -> None:
    """Verify ValidationService run execution and database persistence."""
    config = {"file_path": sample_ai4i_file}

    async with TestSessionLocal() as session:
        user = User(
            email=f"val-user-{uuid.uuid4().hex[:6]}@sentinel-ai.io",
            hashed_password="hashed_secret",
            full_name="Validation User",
        )
        session.add(user)
        await session.flush()

        dataset = Dataset(name="Validation AI4I", owner_id=user.id)
        session.add(dataset)
        await session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            storage_path=sample_ai4i_file,
        )
        session.add(version)
        await session.flush()

        run_repo = ValidationRunRepository(session)
        res_repo = ValidationResultRepository(session)
        val_service = ValidationService(run_repository=run_repo, result_repository=res_repo)

        # Execute and Persist Validation Run
        db_run = await val_service.run_and_persist(version.id, ConnectorType.CSV, config)
        assert db_run.id is not None
        assert db_run.overall_score > 0.0
        assert db_run.status in (RunStatus.FAILED, RunStatus.COMPLETED)
