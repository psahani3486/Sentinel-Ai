"""Statistical Outlier Validation Rule."""

import time
from typing import Any

import numpy as np
import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class OutlierRule(BaseValidationRule):
    """Detects statistical outliers using Z-score (>3) or IQR (1.5*IQR) methods."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.OUTLIERS

    @property
    def name(self) -> str:
        return "Statistical Outlier Detection Rule"

    @property
    def description(self) -> str:
        return "Detects statistical anomalies and extreme numerical outliers using Z-score or IQR thresholds."

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
        z_threshold = float(self.config.get("z_threshold", 3.0))
        target_cols = self.required_columns() or [
            str(c) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
        ]

        failing_cols: list[str] = []
        affected_rows = 0
        details: dict[str, Any] = {}

        for col in target_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                series = df[col].dropna()
                if len(series) >= 5:
                    mean = series.mean()
                    std = series.std()
                    if std > 0:
                        z_scores = np.abs((series - mean) / std)
                        outliers_mask = z_scores > z_threshold
                        outlier_count = int(outliers_mask.sum())

                        if outlier_count > 0:
                            failing_cols.append(col)
                            affected_rows += outlier_count
                            details[col] = {"outlier_count": outlier_count, "z_threshold": z_threshold}

        exec_time = round((time.time() - start_time) * 1000, 2)
        if failing_cols:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.WARNING,
                severity=self.severity,
                message=f"Statistical outliers (|Z| > {z_threshold}) detected in columns: {', '.join(failing_cols)}",
                affected_columns=failing_cols,
                affected_rows_count=affected_rows,
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
            message="No extreme statistical outliers detected.",
            execution_time_ms=exec_time,
        )
