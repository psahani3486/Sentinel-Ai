"""Constant Column Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class ConstantColumnRule(BaseValidationRule):
    """Flags single-value zero-variance columns in dataset."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.CONSTANT_COLUMNS

    @property
    def name(self) -> str:
        return "Constant Single-Value Column Rule"

    @property
    def description(self) -> str:
        return "Flags zero-variance columns that contain only 1 distinct unique value across all rows."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.MEDIUM

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.STATISTICAL

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        constant_cols = [
            str(col) for col in df.columns if df[col].nunique(dropna=True) == 1
        ]

        exec_time = round((time.time() - start_time) * 1000, 2)
        if constant_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.WARNING,
                severity=self.severity,
                message=f"Constant zero-variance columns detected: {', '.join(constant_cols)}",
                affected_columns=constant_cols,
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=10.0,
                details={"constant_columns": constant_cols},
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="No constant zero-variance columns detected.",
            execution_time_ms=exec_time,
        )
