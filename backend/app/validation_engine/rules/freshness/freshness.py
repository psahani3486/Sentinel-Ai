"""Data Freshness SLA Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class FreshnessRule(BaseValidationRule):
    """Asserts that the latest timestamp in the dataset satisfies freshness SLA bounds."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.FRESHNESS_VALIDATION

    @property
    def name(self) -> str:
        return "Data Freshness SLA Rule"

    @property
    def description(self) -> str:
        return "Ensures the latest timestamp in the dataset is within allowed lag bounds (max_lag_hours)."

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
        max_lag_hours = float(self.config.get("max_lag_hours", 24.0))

        # Find timestamp column
        ts_cols = self.required_columns() or [
            str(c)
            for c in df.columns
            if any(kw in str(c).lower() for kw in ["time", "date", "timestamp"])
        ]

        exec_time = round((time.time() - start_time) * 1000, 2)
        if not ts_cols or ts_cols[0] not in df.columns:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.PASSED,
                severity=self.severity,
                message="No timestamp column found to evaluate freshness SLA.",
                execution_time_ms=exec_time,
            )

        ts_col = ts_cols[0]
        dt_series = pd.to_datetime(df[ts_col], errors="coerce").dropna()

        if dt_series.empty:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Timestamp column '{ts_col}' contains no parseable dates to evaluate freshness.",
                affected_columns=[ts_col],
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=15.0,
            )

        latest_dt = dt_series.max()
        details = {
            "timestamp_column": ts_col,
            "latest_timestamp": latest_dt.isoformat(),
            "max_lag_hours": max_lag_hours,
        }

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message=f"Freshness check satisfied. Latest timestamp: {latest_dt.isoformat()}",
            execution_time_ms=exec_time,
            details=details,
        )
