"""Data Completeness Overall SLA Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class DataCompletenessRule(BaseValidationRule):
    """Asserts overall dataset cell density against a required completeness SLA percentage."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.DATA_COMPLETENESS

    @property
    def name(self) -> str:
        return "Data Completeness SLA Rule"

    @property
    def description(self) -> str:
        return "Ensures that the overall dataset non-null cell ratio satisfies the target SLA."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.CRITICAL

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.COMPLETENESS

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        target_sla_pct = float(self.config.get("min_completeness_pct", 95.0))

        total_cells = len(df) * len(df.columns)
        null_cells = int(df.isnull().sum().sum())
        non_null_cells = total_cells - null_cells

        actual_completeness_pct = (
            round((non_null_cells / total_cells) * 100, 2) if total_cells > 0 else 100.0
        )
        exec_time = round((time.time() - start_time) * 1000, 2)

        details = {
            "total_cells": total_cells,
            "null_cells": null_cells,
            "actual_completeness_pct": actual_completeness_pct,
            "target_sla_pct": target_sla_pct,
        }

        if actual_completeness_pct < target_sla_pct:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.FAILED,
                severity=self.severity,
                message=f"Dataset completeness SLA failed ({actual_completeness_pct}% < {target_sla_pct}%).",
                affected_columns=list(df.columns),
                affected_rows_count=null_cells,
                execution_time_ms=exec_time,
                score_impact=25.0,
                details=details,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message=f"Dataset completeness SLA satisfied ({actual_completeness_pct}% >= {target_sla_pct}%).",
            affected_columns=[],
            affected_rows_count=0,
            execution_time_ms=exec_time,
            score_impact=0.0,
            details=details,
        )
