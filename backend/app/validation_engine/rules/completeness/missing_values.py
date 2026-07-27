"""Missing Values Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class MissingValuesRule(BaseValidationRule):
    """Validates that null/missing values in target columns do not exceed threshold ratios."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.MISSING_VALUES

    @property
    def name(self) -> str:
        return "Missing Values Rule"

    @property
    def description(self) -> str:
        return "Checks that the ratio or count of missing/null values stays within allowed limits."

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
        max_null_pct = float(self.config.get("max_null_percentage", 5.0))
        target_cols = self.required_columns() or list(df.columns)

        failing_cols: list[str] = []
        affected_rows = 0
        details: dict[str, Any] = {}

        for col in target_cols:
            if col in df.columns:
                null_count = int(df[col].isnull().sum())
                total_count = len(df)
                null_pct = (null_count / total_count * 100) if total_count > 0 else 0.0

                details[col] = {"null_count": null_count, "null_percentage": round(null_pct, 2)}
                if null_pct > max_null_pct:
                    failing_cols.append(col)
                    affected_rows += null_count

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Missing value threshold ({max_null_pct}%) exceeded in columns: {', '.join(failing_cols)}",
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
            message="All columns satisfied missing value thresholds.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details=details,
        )
