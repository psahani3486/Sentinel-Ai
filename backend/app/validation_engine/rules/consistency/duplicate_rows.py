"""Duplicate Rows Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class DuplicateRowsRule(BaseValidationRule):
    """Detects duplicate rows across full records or a subset of key columns."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.DUPLICATE_ROWS

    @property
    def name(self) -> str:
        return "Duplicate Rows Rule"

    @property
    def description(self) -> str:
        return "Identifies duplicate records exceeding configured tolerance thresholds."

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
        max_dup_pct = float(self.config.get("max_duplicate_percentage", 1.0))
        subset_cols = self.required_columns() or None

        dup_mask = df.duplicated(subset=subset_cols)
        dup_count = int(dup_mask.sum())
        total_rows = len(df)
        dup_pct = (dup_count / total_rows * 100) if total_rows > 0 else 0.0

        exec_time = round((time.time() - start_time) * 1000, 2)
        details = {
            "duplicate_count": dup_count,
            "duplicate_percentage": round(dup_pct, 2),
            "max_duplicate_percentage": max_dup_pct,
        }

        if dup_pct > max_dup_pct:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Duplicate rows threshold exceeded ({round(dup_pct, 2)}% > {max_dup_pct}%). Count: {dup_count}",
                affected_columns=subset_cols or list(df.columns),
                affected_rows_count=dup_count,
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
            message="Duplicate rows ratio within acceptable limits.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details=details,
        )
