"""
Sentinel AI — Rule Executor

Isolated execution context for validation rules. Ensures rules execute independently
and safely without cascading failures or inter-rule state mutation.
"""

import logging
import time
from typing import Any

import pandas as pd

from app.models.enums import ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import BaseValidationRule, RuleResult

logger = logging.getLogger(__name__)


class RuleExecutor:
    """Executes single or batches of validation rules independently."""

    @staticmethod
    def execute_rule(
        rule: BaseValidationRule,
        df: pd.DataFrame,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        """
        Safely execute a single validation rule.

        Catches unexpected runtime exceptions and converts them into structured RuleResult ERROR states.
        """
        start_time = time.time()
        try:
            result = rule.validate(df, schema_info=schema_info, history=history)
            logger.info("Executed rule '%s' -> Status: %s", rule.name, result.status.value)
            return result
        except Exception as e:
            exec_time = round((time.time() - start_time) * 1000, 2)
            logger.error("Exception during rule execution '%s': %s", rule.name, str(e), exc_info=True)
            return RuleResult(
                rule_name=rule.name,
                rule_type=rule.rule_type,
                category=rule.category,
                status=ValidationStatus.ERROR,
                severity=rule.severity or ValidationSeverity.HIGH,
                message=f"Execution error in rule '{rule.name}': {str(e)}",
                execution_time_ms=exec_time,
                score_impact=15.0,
                details={"error": str(e)},
            )
