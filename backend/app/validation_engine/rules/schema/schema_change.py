"""Schema Change Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class SchemaChangeRule(BaseValidationRule):
    """Detects missing columns or unexpected new columns compared to expected baseline schema."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.SCHEMA_CHANGES

    @property
    def name(self) -> str:
        return "Schema Drift & Structural Change Rule"

    @property
    def description(self) -> str:
        return "Detects unexpected column additions, missing columns, or structural header drift."

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
        expected_columns: list[str] = self.config.get("expected_columns", [])

        if not expected_columns and schema_info:
            expected_columns = [s["column_name"] for s in schema_info]

        exec_time = round((time.time() - start_time) * 1000, 2)
        if not expected_columns:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.PASSED,
                severity=self.severity,
                message="No expected baseline columns configured for schema drift assertion.",
                execution_time_ms=exec_time,
            )

        actual_set = set(str(c) for c in df.columns)
        expected_set = set(expected_columns)

        missing_cols = list(expected_set - actual_set)
        added_cols = list(actual_set - expected_set)

        details = {"missing_columns": missing_cols, "added_columns": added_cols}

        if missing_cols or added_cols:
            msg_parts = []
            if missing_cols:
                msg_parts.append(f"Missing columns: {', '.join(missing_cols)}")
            if added_cols:
                msg_parts.append(f"New unexpected columns: {', '.join(added_cols)}")

            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message="Schema drift detected! " + "; ".join(msg_parts),
                affected_columns=missing_cols + added_cols,
                affected_rows_count=len(df),
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
            message="Schema matches baseline configuration perfectly.",
            execution_time_ms=exec_time,
            details=details,
        )
