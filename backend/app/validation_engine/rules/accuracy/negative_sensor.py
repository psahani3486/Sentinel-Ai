"""Negative Sensor Value Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class NegativeSensorValueRule(BaseValidationRule):
    """Flags illegal negative values in physical sensor channels (speed, pressure, temperature in Kelvin, torque, wear)."""

    SENSOR_KEYWORDS = ["rpm", "speed", "temp", "temperature", "pressure", "wear", "torque", "rotational"]

    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEGATIVE_SENSOR_VALUES

    @property
    def name(self) -> str:
        return "Negative Sensor Value Rule"

    @property
    def description(self) -> str:
        return "Flags non-physical negative values in positive sensor measurements."

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
        configured_cols = self.required_columns()

        if not configured_cols:
            configured_cols = [
                str(col)
                for col in df.columns
                if pd.api.types.is_numeric_dtype(df[col])
                and any(kw in str(col).lower() for kw in self.SENSOR_KEYWORDS)
            ]

        failing_cols: list[str] = []
        affected_rows = 0
        details: dict[str, Any] = {}

        for col in configured_cols:
            if col in df.columns:
                neg_mask = df[col] < 0.0
                neg_count = int(neg_mask.sum())
                if neg_count > 0:
                    failing_cols.append(col)
                    affected_rows += neg_count
                    details[col] = {"negative_count": neg_count}

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Negative sensor values detected in physical columns: {', '.join(failing_cols)}",
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
            message="No illegal negative sensor values detected.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details={},
        )
