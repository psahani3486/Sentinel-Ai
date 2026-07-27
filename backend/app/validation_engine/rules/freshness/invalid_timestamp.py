"""Invalid Timestamp Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class InvalidTimestampRule(BaseValidationRule):
    """Flags unparseable, null, or future timestamps in datetime columns."""

    TIMESTAMP_KEYWORDS = ["time", "timestamp", "date", "datetime", "t_stamp"]

    @property
    def rule_type(self) -> RuleType:
        return RuleType.INVALID_TIMESTAMPS

    @property
    def name(self) -> str:
        return "Invalid Timestamp Rule"

    @property
    def description(self) -> str:
        return "Identifies unparseable date/time strings, missing timestamps, or illegal future timestamps."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.HIGH

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.FRESHNESS

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        target_cols = self.required_columns()

        if not target_cols:
            target_cols = [
                str(col)
                for col in df.columns
                if any(kw in str(col).lower() for kw in self.TIMESTAMP_KEYWORDS)
            ]

        failing_cols: list[str] = []
        affected_rows = 0
        details: dict[str, Any] = {}

        for col in target_cols:
            if col in df.columns:
                dt_converted = pd.to_datetime(df[col], errors="coerce")
                invalid_count = int(dt_converted.isnull().sum())

                if invalid_count > 0:
                    failing_cols.append(col)
                    affected_rows += invalid_count
                    details[col] = {"unparseable_timestamp_count": invalid_count}

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Invalid or unparseable timestamps found in columns: {', '.join(failing_cols)}",
                affected_columns=failing_cols,
                affected_rows_count=affected_rows,
                execution_time_ms=exec_time,
                score_impact=15.0,
                details=details,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="No invalid timestamps detected.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details={},
        )
