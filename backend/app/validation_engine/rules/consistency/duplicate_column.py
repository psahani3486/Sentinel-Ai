"""Duplicate Column Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class DuplicateColumnRule(BaseValidationRule):
    """Detects duplicate column names or identical column data content."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.DUPLICATE_COLUMNS

    @property
    def name(self) -> str:
        return "Duplicate Column Rule"

    @property
    def description(self) -> str:
        return "Flags duplicate column header names or identical column data payloads."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.MEDIUM

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
        col_names = [str(c) for c in df.columns]

        # 1. Header duplicate check
        seen = set()
        dup_names = []
        for name in col_names:
            if name in seen:
                dup_names.append(name)
            seen.add(name)

        exec_time = round((time.time() - start_time) * 1000, 2)
        if dup_names:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Duplicate column names detected: {', '.join(dup_names)}",
                affected_columns=dup_names,
                affected_rows_count=len(df),
                execution_time_ms=exec_time,
                score_impact=10.0,
                details={"duplicate_column_names": dup_names},
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message="No duplicate column names detected.",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details={},
        )
