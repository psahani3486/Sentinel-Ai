"""Primary Key Constraint Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class PrimaryKeyRule(BaseValidationRule):
    """Ensures designated primary key column(s) have 0 nulls and 100% uniqueness."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.PRIMARY_KEY_VALIDATION

    @property
    def name(self) -> str:
        return "Primary Key Constraint Rule"

    @property
    def description(self) -> str:
        return "Asserts that configured primary key columns contain 0 nulls and 100% unique values."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.CRITICAL

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
        pk_cols = self.required_columns()

        if not pk_cols:
            pk_cols = [
                str(c)
                for c in df.columns
                if str(c).lower() in ["udi", "id", "unit_number", "product_id", "product id"]
            ]

        exec_time = round((time.time() - start_time) * 1000, 2)
        if not pk_cols or not all(c in df.columns for c in pk_cols):
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.PASSED,
                severity=self.severity,
                message="No valid primary key column configured for assertion.",
                execution_time_ms=exec_time,
            )

        # Check nulls
        null_count = int(df[pk_cols].isnull().any(axis=1).sum())
        # Check duplicates
        dup_count = int(df.duplicated(subset=pk_cols).sum())

        details = {"primary_key_columns": pk_cols, "null_count": null_count, "duplicate_count": dup_count}

        if null_count > 0 or dup_count > 0:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Primary key violation in {pk_cols}! Null count: {null_count}, Duplicates: {dup_count}",
                affected_columns=pk_cols,
                affected_rows_count=null_count + dup_count,
                execution_time_ms=exec_time,
                score_impact=25.0,
                details=details,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message=f"Primary key constraint satisfied on columns: {', '.join(pk_cols)}",
            execution_time_ms=exec_time,
            details=details,
        )
