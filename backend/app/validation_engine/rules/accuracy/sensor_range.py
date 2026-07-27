"""Sensor Range Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class SensorRangeRule(BaseValidationRule):
    """Validates numeric sensor values against operational minimum and maximum limits."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.INVALID_SENSOR_RANGE

    @property
    def name(self) -> str:
        return "Sensor Operational Range Rule"

    @property
    def description(self) -> str:
        return "Ensures sensor telemetry values remain within configured physical operational min/max bounds."

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
        ranges: dict[str, dict[str, float]] = self.config.get("ranges", {})

        # Default AI4I bounds if none explicitly configured
        if not ranges:
            for col in df.columns:
                col_lower = str(col).lower()
                if "air temperature" in col_lower:
                    ranges[str(col)] = {"min": 250.0, "max": 350.0}
                elif "process temperature" in col_lower:
                    ranges[str(col)] = {"min": 250.0, "max": 360.0}
                elif "rotational speed" in col_lower:
                    ranges[str(col)] = {"min": 500.0, "max": 3000.0}
                elif "torque" in col_lower:
                    ranges[str(col)] = {"min": 0.0, "max": 150.0}

        failing_cols: list[str] = []
        affected_rows = 0
        details: dict[str, Any] = {}

        for col, bound in ranges.items():
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                min_val = bound.get("min", float("-inf"))
                max_val = bound.get("max", float("inf"))

                out_of_bounds = df[(df[col] < min_val) | (df[col] > max_val)]
                oob_count = len(out_of_bounds)

                if oob_count > 0:
                    failing_cols.append(col)
                    affected_rows += oob_count
                    details[col] = {
                        "out_of_bounds_count": oob_count,
                        "min_bound": min_val,
                        "max_bound": max_val,
                    }

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Sensor values exceeded operational bounds in columns: {', '.join(failing_cols)}",
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
            message="All configured sensors operate within valid bounds.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details=details,
        )
