"""Data Accuracy SLA Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class DataAccuracyRule(BaseValidationRule):
    """Evaluates overall dataset measurement accuracy and sensor deadlock states."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.DATA_ACCURACY

    @property
    def name(self) -> str:
        return "Data Accuracy SLA Rule"

    @property
    def description(self) -> str:
        return "Asserts overall measurement accuracy and detects sensor flatlining/deadlock states."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.CRITICAL

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
        deadlocked_sensors: list[str] = []

        # Check for zero-variance numeric sensors (deadlocked telemetry channels)
        if len(df) > 2:
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_str = str(col).lower()
                    if "sensor" in col_str or "temp" in col_str or "speed" in col_str:
                        if df[col].nunique(dropna=True) == 1:
                            deadlocked_sensors.append(str(col))

        exec_time = round((time.time() - start_time) * 1000, 2)
        if deadlocked_sensors:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Sensor flatlining / accuracy deadlock detected in channels: {', '.join(deadlocked_sensors)}",
                affected_columns=deadlocked_sensors,
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=25.0,
                details={"deadlocked_sensors": deadlocked_sensors},
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="Data accuracy and sensor telemetry variance check satisfied.",
            execution_time_ms=exec_time,
        )
