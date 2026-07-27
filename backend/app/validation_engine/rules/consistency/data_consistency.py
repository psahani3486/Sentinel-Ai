"""Data Consistency Rule (Cross-Column Boolean Assertions)."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class DataConsistencyRule(BaseValidationRule):
    """Validates cross-column boolean logic (e.g. process_temp > air_temp)."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.DATA_CONSISTENCY

    @property
    def name(self) -> str:
        return "Data Consistency Rule"

    @property
    def description(self) -> str:
        return "Validates relationship invariants and cross-column logic assertions."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.HIGH

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.CONSISTENCY

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        expression = self.config.get("expression")

        # Auto-detect Process vs Air temperature in AI4I if no expression configured
        if not expression:
            air_col = next((c for c in df.columns if "Air temperature" in str(c)), None)
            proc_col = next((c for c in df.columns if "Process temperature" in str(c)), None)
            if air_col and proc_col:
                expression = f"`{proc_col}` >= `{air_col}`"

        if not expression:
            exec_time = round((time.time() - start_time) * 1000, 2)
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.PASSED,
                severity=self.severity,
                message="No cross-column consistency expression defined or matched.",
                execution_time_ms=exec_time,
            )

        try:
            valid_mask = df.eval(expression)
            failing_rows = int((~valid_mask).sum())
            exec_time = round((time.time() - start_time) * 1000, 2)

            if failing_rows > 0:
                return RuleResult(
                    rule_name=self.name,
                    rule_type=self.rule_type,
                    category=self.category,
                    status=ValidationStatus.FAILED,
                    severity=self.severity,
                    message=f"Cross-column consistency assertion '{expression}' failed on {failing_rows} rows.",
                    affected_columns=self.required_columns(),
                    affected_rows_count=failing_rows,
                    execution_time_ms=exec_time,
                    score_impact=15.0,
                    details={"expression": expression, "failing_rows_count": failing_rows},
                )
        except Exception as e:
            exec_time = round((time.time() - start_time) * 1000, 2)
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.ERROR,
                severity=self.severity,
                message=f"Failed to evaluate consistency expression '{expression}': {str(e)}",
                execution_time_ms=exec_time,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message=f"Cross-column consistency assertion '{expression}' passed cleanly.",
            execution_time_ms=exec_time,
        )
