"""Unique Constraint Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class UniqueConstraintRule(BaseValidationRule):
    """Asserts uniqueness across defined composite column sets."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.UNIQUE_CONSTRAINT_VALIDATION

    @property
    def name(self) -> str:
        return "Unique Constraint Rule"

    @property
    def description(self) -> str:
        return "Ensures that configured single or multi-column combinations contain zero duplicate tuples."

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
        unique_cols = self.required_columns()

        exec_time = round((time.time() - start_time) * 1000, 2)
        if not unique_cols or not all(c in df.columns for c in unique_cols):
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.PASSED,
                severity=self.severity,
                message="No valid unique constraint columns configured.",
                execution_time_ms=exec_time,
            )

        dup_mask = df.duplicated(subset=unique_cols, keep=False)
        dup_count = int(dup_mask.sum())

        if dup_count > 0:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Unique constraint violated on column set {unique_cols}! Duplicates: {dup_count}",
                affected_columns=unique_cols,
                affected_rows_count=dup_count,
                execution_time_ms=exec_time,
                score_impact=15.0,
                details={"unique_columns": unique_cols, "duplicate_count": dup_count},
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message=f"Unique constraint satisfied for column set: {', '.join(unique_cols)}",
            execution_time_ms=exec_time,
        )
