"""Null Column Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class NullColumnRule(BaseValidationRule):
    """Detects completely empty (100% null) columns in the dataset."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.NULL_COLUMNS

    @property
    def name(self) -> str:
        return "Null Column Rule"

    @property
    def description(self) -> str:
        return "Flags columns that contain zero non-null values."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.HIGH

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.COMPLETENESS

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        null_cols = [str(col) for col in df.columns if df[col].isnull().all()]

        exec_time = round((time.time() - start_time) * 1000, 2)
        if null_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Completely null columns detected: {', '.join(null_cols)}",
                affected_columns=null_cols,
                affected_rows_count=len(df) * len(null_cols),
                execution_time_ms=exec_time,
                score_impact=15.0,
                details={"null_columns": null_cols},
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="No completely null columns detected.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details={},
        )
