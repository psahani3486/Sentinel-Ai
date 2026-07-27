"""Invalid Numeric Validation Rule."""

import time
from typing import Any

import numpy as np
import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class InvalidNumericRule(BaseValidationRule):
    """Flags non-numeric values, NaN, or Inf in numeric columns."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.INVALID_NUMERIC_VALUES

    @property
    def name(self) -> str:
        return "Invalid Numeric Value Rule"

    @property
    def description(self) -> str:
        return "Detects unparseable non-numeric, NaN, or infinite floating point values in numeric features."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.HIGH

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.ACCURACY

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        target_cols = self.required_columns() or [
            str(c) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
        ]

        failing_cols: list[str] = []
        affected_rows = 0
        details: dict[str, Any] = {}

        for col in target_cols:
            if col in df.columns:
                series = pd.to_numeric(df[col], errors="coerce")
                nan_count = int(series.isnull().sum())
                inf_count = int(np.isinf(series.dropna()).sum())
                invalid_total = inf_count + nan_count

                if invalid_total > 0:
                    failing_cols.append(col)
                    affected_rows += invalid_total
                    details[col] = {"inf_count": inf_count, "nan_count": nan_count}

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Invalid numeric (NaN/Inf) values found in columns: {', '.join(failing_cols)}",
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
            message="No invalid numeric (NaN/Inf) values detected.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details={},
        )
