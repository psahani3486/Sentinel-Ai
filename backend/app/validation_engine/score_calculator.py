"""
Sentinel AI — Quality Score Calculator

Computes weighted Data Quality Scores (0-100) overall and across individual quality categories:
Completeness, Consistency, Accuracy, Freshness, Schema, and Statistical quality.
"""

from typing import Any

from app.models.enums import ValidationSeverity, ValidationStatus
from app.validation_engine.base_rule import RuleCategory, RuleResult


class ScoreCalculator:
    """Calculates weighted Data Quality Scores from rule execution results."""

    DEFAULT_CATEGORY_WEIGHTS: dict[RuleCategory, float] = {
        RuleCategory.COMPLETENESS: 0.25,
        RuleCategory.ACCURACY: 0.25,
        RuleCategory.CONSISTENCY: 0.20,
        RuleCategory.SCHEMA: 0.15,
        RuleCategory.FRESHNESS: 0.10,
        RuleCategory.STATISTICAL: 0.05,
    }

    SEVERITY_PENALTIES: dict[ValidationSeverity, float] = {
        ValidationSeverity.CRITICAL: 25.0,
        ValidationSeverity.HIGH: 15.0,
        ValidationSeverity.MEDIUM: 10.0,
        ValidationSeverity.LOW: 5.0,
        ValidationSeverity.INFO: 0.0,
    }

    def __init__(
        self,
        category_weights: dict[RuleCategory, float] | None = None,
        severity_penalties: dict[ValidationSeverity, float] | None = None,
    ) -> None:
        self.weights = category_weights or self.DEFAULT_CATEGORY_WEIGHTS
        self.penalties = severity_penalties or self.SEVERITY_PENALTIES

    def calculate_scores(self, results: list[RuleResult]) -> dict[str, Any]:
        """
        Calculate overall and per-category data quality scores (0.0 to 100.0).

        Returns:
            Dict containing overall_score, category_scores, passed_rules_count,
            failed_rules_count, error_rules_count, and total_rules_count.
        """
        if not results:
            return {
                "overall_score": 100.0,
                "category_scores": {cat.value: 100.0 for cat in RuleCategory},
                "passed_rules_count": 0,
                "failed_rules_count": 0,
                "error_rules_count": 0,
                "total_rules_count": 0,
            }

        # Group results by category
        results_by_cat: dict[RuleCategory, list[RuleResult]] = {cat: [] for cat in RuleCategory}
        for res in results:
            results_by_cat[res.category].append(res)

        category_scores: dict[str, float] = {}

        for cat, cat_results in results_by_cat.items():
            if not cat_results:
                category_scores[cat.value] = 100.0
                continue

            total_penalty = 0.0
            for res in cat_results:
                if res.status in (ValidationStatus.FAILED, ValidationStatus.ERROR):
                    penalty = self.penalties.get(res.severity, 10.0)
                    total_penalty += penalty
                elif res.status == ValidationStatus.WARNING:
                    penalty = self.penalties.get(res.severity, 5.0) * 0.5
                    total_penalty += penalty

            cat_score = max(0.0, 100.0 - total_penalty)
            category_scores[cat.value] = round(cat_score, 2)

        # Overall Weighted Score
        weighted_sum = 0.0
        weight_total = 0.0

        for cat, weight in self.weights.items():
            score = category_scores.get(cat.value, 100.0)
            weighted_sum += score * weight
            weight_total += weight

        overall_score = round(weighted_sum / weight_total, 2) if weight_total > 0 else 100.0

        passed_count = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed_count = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        error_count = sum(1 for r in results if r.status == ValidationStatus.ERROR)

        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "passed_rules_count": passed_count,
            "failed_rules_count": failed_count,
            "error_rules_count": error_count,
            "total_rules_count": len(results),
        }
