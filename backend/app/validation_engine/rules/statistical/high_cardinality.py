"""High Cardinality Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class HighCardinalityRule(BaseValidationRule):
    """Flags non-identifier categorical/string columns exceeding cardinality thresholds (>80% unique)."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.HIGH_CARDINALITY

    @property
    def name(self) -> str:
        return "High Cardinality Column Rule"

    @property
    def description(self) -> str:
        return "Flags non-primary-key categorical columns with excessively high distinct value ratios."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.LOW

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
        max_unique_pct = float(self.config.get("max_unique_pct", 80.0))
        total_rows = len(df)

        failing_cols: list[str] = []
        details: dict[str, Any] = {}

        if total_rows > 10:
            for col in df.columns:
                col_str = str(col)
                if not pd.api.types.is_numeric_dtype(df[col]) and not col_str.lower().endswith("id"):
                    unique_count = int(df[col].nunique(dropna=True))
                    unique_pct = (unique_count / total_rows) * 100

                    if unique_pct > max_unique_pct and unique_count < total_rows:
                        failing_cols.append(col_str)
                        details[col_str] = {"unique_count": unique_count, "unique_percentage": round(unique_pct, 2)}

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.WARNING,
                severity=self.severity,
                message=f"High cardinality categorical columns detected: {', '.join(failing_cols)}",
                affected_columns=failing_cols,
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=5.0,
                details=details,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="No high cardinality anomalies detected.",
            execution_time_ms=exec_time,
        )
