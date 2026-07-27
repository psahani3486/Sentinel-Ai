"""Low Cardinality Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class LowCardinalityRule(BaseValidationRule):
    """Flags numeric features with unexpectedly low distinct unique values (<5 unique)."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.LOW_CARDINALITY

    @property
    def name(self) -> str:
        return "Low Cardinality Feature Rule"

    @property
    def description(self) -> str:
        return "Flags continuous numeric channels with suspiciously low distinct unique values."

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
        min_unique_count = int(self.config.get("min_unique_count", 5))

        failing_cols: list[str] = []
        details: dict[str, Any] = {}

        if len(df) > 20:
            for col in df.columns:
                col_str = str(col)
                if pd.api.types.is_numeric_dtype(df[col]) and not col_str.lower().endswith("failure"):
                    unique_count = int(df[col].nunique(dropna=True))
                    if 1 < unique_count < min_unique_count:
                        failing_cols.append(col_str)
                        details[col_str] = {"unique_count": unique_count}

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.WARNING,
                severity=self.severity,
                message=f"Low cardinality numeric features (< {min_unique_count} unique) detected: {', '.join(failing_cols)}",
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
            message="No low cardinality numeric anomalies detected.",
            execution_time_ms=exec_time,
        )
