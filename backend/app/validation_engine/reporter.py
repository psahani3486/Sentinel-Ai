"""
Sentinel AI — Validation Reporter

Generates comprehensive validation execution reports and historical trend comparisons.
Detects improvements (resolved failures) and regressions (new failures) across runs.
"""

from typing import Any

from app.models.enums import ValidationStatus
from app.validation_engine.base_rule import RuleResult


class ValidationReporter:
    """Formats validation reports and calculates historical comparisons."""

    @staticmethod
    def generate_report(
        results: list[RuleResult],
        scores: dict[str, Any],
        total_execution_time_ms: float,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Build a comprehensive validation report dictionary.

        Args:
            results: List of RuleResult objects from the current run.
            scores: Quality score dictionary from ScoreCalculator.
            total_execution_time_ms: Total engine execution time in milliseconds.
            history: Optional list of past validation run result dictionaries.

        Returns:
            Dict containing summary, passed_rules, failed_rules, warnings, severity_distribution,
            affected_columns, affected_rows, and historical_comparison.
        """
        passed_rules: list[dict[str, Any]] = []
        failed_rules: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        affected_cols_set: set[str] = set()
        total_affected_rows = 0

        severity_dist: dict[str, int] = {}

        for res in results:
            res_dict = res.model_dump()
            sev_str = res.severity.value if hasattr(res.severity, "value") else str(res.severity)
            severity_dist[sev_str] = severity_dist.get(sev_str, 0) + 1

            for col in res.affected_columns:
                affected_cols_set.add(col)

            total_affected_rows += res.affected_rows_count

            if res.status == ValidationStatus.PASSED:
                passed_rules.append(res_dict)
            elif res.status in (ValidationStatus.FAILED, ValidationStatus.ERROR):
                failed_rules.append(res_dict)
            elif res.status == ValidationStatus.WARNING:
                warnings.append(res_dict)

        # Historical Comparison
        historical_comparison = ValidationReporter.compare_with_history(results, history)

        return {
            "summary": {
                "overall_score": scores.get("overall_score", 100.0),
                "total_rules_executed": len(results),
                "passed_count": scores.get("passed_rules_count", 0),
                "failed_count": scores.get("failed_count", 0),
                "error_count": scores.get("error_count", 0),
                "total_execution_time_ms": round(total_execution_time_ms, 2),
                "affected_columns_count": len(affected_cols_set),
                "total_affected_rows": total_affected_rows,
            },
            "category_scores": scores.get("category_scores", {}),
            "severity_distribution": severity_dist,
            "affected_columns": list(affected_cols_set),
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "warnings": warnings,
            "historical_comparison": historical_comparison,
        }

    @staticmethod
    def compare_with_history(
        current_results: list[RuleResult], history: list[dict[str, Any]] | None
    ) -> dict[str, Any]:
        """
        Compare current run results against the most recent historical run.

        Returns:
            Dict containing improvements (resolved failures), regressions (new failures),
            score_delta, and trend status ('IMPROVED', 'REGRESSED', 'STABLE').
        """
        if not history:
            return {
                "has_previous_run": False,
                "improvements": [],
                "regressions": [],
                "score_delta": 0.0,
                "status": "STABLE",
            }

        prev_run = history[0]  # Most recent past run
        prev_failed_rules = set()

        for r in prev_run.get("failed_rules", []):
            st = str(r.get("status", "")).lower()
            if st in (ValidationStatus.FAILED.value.lower(), ValidationStatus.ERROR.value.lower()):
                prev_failed_rules.add(r.get("rule_name"))

        curr_failed_rules = {
            r.rule_name
            for r in current_results
            if r.status in (ValidationStatus.FAILED, ValidationStatus.ERROR)
        }

        resolved_failures = list(prev_failed_rules - curr_failed_rules)
        new_failures = list(curr_failed_rules - prev_failed_rules)

        prev_score = prev_run.get("summary", {}).get("overall_score", 100.0)
        curr_score = next(
            (r.score_impact for r in current_results), 100.0
        )

        score_delta = round(curr_score - prev_score, 2)

        if len(new_failures) > len(resolved_failures):
            status = "REGRESSED"
        elif len(resolved_failures) > len(new_failures):
            status = "IMPROVED"
        else:
            status = "STABLE"

        return {
            "has_previous_run": True,
            "previous_run_timestamp": prev_run.get("timestamp"),
            "improvements": resolved_failures,
            "regressions": new_failures,
            "score_delta": score_delta,
            "status": status,
        }
