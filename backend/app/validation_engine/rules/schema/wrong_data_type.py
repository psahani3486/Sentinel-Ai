"""Wrong Data Type Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class WrongDataTypeRule(BaseValidationRule):
    """Flags data type mismatches between expected schema types and actual DataFrame dtypes."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.WRONG_DATA_TYPES

    @property
    def name(self) -> str:
        return "Wrong Data Type Rule"

    @property
    def description(self) -> str:
        return "Flags data type drift where actual column dtypes mismatch expected schema specifications."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.HIGH

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.SCHEMA

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        expected_types: dict[str, str] = self.config.get("expected_types", {})

        if not expected_types and schema_info:
            for s in schema_info:
                expected_types[s["column_name"]] = s.get("data_type", "str")

        mismatches: list[dict[str, Any]] = []
        failing_cols: list[str] = []

        for col, expected in expected_types.items():
            if col in df.columns:
                actual = str(df[col].dtype)
                if expected.lower() in ["int", "float", "numeric"] and not pd.api.types.is_numeric_dtype(df[col]):
                    mismatches.append({"column": col, "expected": expected, "actual": actual})
                    failing_cols.append(col)

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Data type mismatches detected in columns: {', '.join(failing_cols)}",
                affected_columns=failing_cols,
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=15.0,
                details={"mismatches": mismatches},
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="No data type mismatches detected.",
            execution_time_ms=exec_time,
        )
