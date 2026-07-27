"""Business Validation Rule."""

import time
from typing import Any

import pandas as pd

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory, RuleResult


class CrossColumnBusinessRule(BaseValidationRule):
    """Executes custom business domain assertions and multi-column invariants."""

    @property
    def rule_type(self) -> RuleType:
        return RuleType.BUSINESS_RULE

    @property
    def name(self) -> str:
        return "Cross-Column Business Domain Rule"

    @property
    def description(self) -> str:
        return "Executes custom domain business logic and multi-column operational assertions."

    @property
    def severity(self) -> ValidationSeverity:
        return ValidationSeverity.HIGH

    @property
    def category(self) -> RuleCategory:
        return RuleCategory.BUSINESS

    def validate(
        self,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        start_time = time.time()
        business_query = self.config.get("business_query")

        # Auto-detect AI4I tool wear failure invariant if no custom query configured
        if not business_query:
            if "Tool wear [min]" in df.columns and "Machine failure" in df.columns:
                business_query = "`Tool wear [min]` >= 0"

        exec_time = round((time.time() - start_time) * 1000, 2)
        if not business_query:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.PASSED,
                severity=self.severity,
                message="No custom business rule query configured.",
                execution_time_ms=exec_time,
            )

        try:
            valid_mask = df.eval(business_query)
            failing_rows = int((~valid_mask).sum())

            if failing_rows > 0:
                return RuleResult(
                    rule_name=self.name,
                    rule_type=self.rule_type,
                    category=self.category,
                    status=ValidationStatus.FAILED,
                    severity=self.severity,
                    message=f"Business rule query '{business_query}' failed on {failing_rows} records.",
                    affected_columns=self.required_columns(),
                    affected_rows_count=failing_rows,
                    execution_time_ms=exec_time,
                    score_impact=15.0,
                    details={"business_query": business_query, "failing_rows_count": failing_rows},
                )
        except Exception as e:
            return RuleResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                category=self.category,
                status=ValidationStatus.ERROR,
                severity=self.severity,
                message=f"Failed to execute business query '{business_query}': {str(e)}",
                execution_time_ms=exec_time,
            )

        return RuleResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            category=self.category,
            status=ValidationStatus.PASSED,
            severity=self.severity,
            message=f"Business rule assertion '{business_query}' satisfied.",
            execution_time_ms=exec_time,
        )
