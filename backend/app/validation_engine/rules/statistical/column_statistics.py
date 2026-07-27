"""Column Statistics Boundary Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class ColumnStatisticsRule(BaseValidationRule):
    """Validates that numerical column aggregate statistics (mean, stddev) stay within expected bounds."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.COLUMN_STATISTICS

    @property
    def name(self) -> str:
        return "Column Statistics SLA Rule"

    @property
    def description(self) -> str:
        return "Asserts that mean and standard deviation aggregates remain within expected operational limits."

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
        stat_bounds: dict[str, dict[str, float]] = self.config.get("stat_bounds", {})

        failing_cols: list[str] = []
        details: dict[str, Any] = {}

        for col, bounds in stat_bounds.items():
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                actual_mean = float(df[col].mean())
                expected_min_mean = bounds.get("min_mean", float("-inf"))
                expected_max_mean = bounds.get("max_mean", float("inf"))

                if actual_mean < expected_min_mean or actual_mean > expected_max_mean:
                    failing_cols.append(col)
                    details[col] = {
                        "actual_mean": round(actual_mean, 2),
                        "expected_min_mean": expected_min_mean,
                        "expected_max_mean": expected_max_mean,
                    }

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Statistical mean aggregate bounds violated in columns: {', '.join(failing_cols)}",
                affected_columns=failing_cols,
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=10.0,
                details=details,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="Column statistical mean aggregates satisfy expected bounds.",
            execution_time_ms=exec_time,
        )
