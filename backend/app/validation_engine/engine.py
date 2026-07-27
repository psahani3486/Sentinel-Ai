"""
Sentinel AI — Validation Engine

Core orchestrator of the Sentinel AI validation pipeline. Loads validation rules,
executes rules via RuleExecutor, calculates Quality Scores via ScoreCalculator,
and compiles structured reports via ValidationReporter.
"""

import logging
import time
from typing import Any

import pandas as pd

from app.validation_engine.base_rule import BaseValidationRule, RuleResult
from app.validation_engine.executor import RuleExecutor
from app.validation_engine.registry import RuleRegistry
from app.validation_engine.reporter import ValidationReporter
from app.validation_engine.score_calculator import ScoreCalculator

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Orchestrates data quality rule execution, score calculation, and reporting."""

    def __init__(
        self,
        score_calculator: ScoreCalculator | None = None,
        reporter: ValidationReporter | None = None,
    ) -> None:
        self.score_calculator = score_calculator or ScoreCalculator()
        self.reporter = reporter or ValidationReporter()

    def run_validations(
        self,
        df: pd.DataFrame,
        rules: list[BaseValidationRule | dict[str, Any]] | None = None,
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Execute validation rules against a dataset payload.

        Args:
            df: Target pandas DataFrame payload.
            rules: List of instantiated rules or rule configuration dictionaries.
            schema_info: Discovered schema metadata if available.
            history: Optional list of past validation run results.

        Returns:
            Dict containing full validation report, scores, and historical trends.
        """
        start_time = time.time()
        executable_rules = self._instantiate_rules(rules)

        logger.info("Executing %d validation rules...", len(executable_rules))
        results: list[RuleResult] = []

        for rule in executable_rules:
            result = RuleExecutor.execute_rule(
                rule, df, schema_info=schema_info, history=history
            )
            results.append(result)

        total_exec_time = (time.time() - start_time) * 1000

        # Calculate Quality Scores
        scores = self.score_calculator.calculate_scores(results)

        # Generate Structured Report
        report = self.reporter.generate_report(
            results, scores, total_exec_time, history=history
        )

        logger.info(
            "Validation run complete. Overall Quality Score: %s/100 (Passed: %d, Failed: %d)",
            scores["overall_score"],
            scores["passed_rules_count"],
            scores["failed_rules_count"],
        )
        return report

    def _instantiate_rules(
        self, rules_input: list[BaseValidationRule | dict[str, Any]] | None
    ) -> list[BaseValidationRule]:
        """Convert rule configs or instances into executable BaseValidationRule objects."""
        if not rules_input:
            # Load default full suite of 21 registered rules
            return [
                RuleRegistry.create(rule_type)
                for rule_type in RuleRegistry.list_supported_rules()
            ]

        executable: list[BaseValidationRule] = []
        for item in rules_input:
            if isinstance(item, BaseValidationRule):
                executable.append(item)
            elif isinstance(item, dict):
                rule_type = item.get("rule_type")
                config = item.get("config", {})
                if rule_type:
                    executable.append(RuleRegistry.create(rule_type, config=config))

        return executable
