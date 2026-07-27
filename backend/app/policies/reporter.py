"""
Sentinel AI — Policy Reporter

Formats policy compliance metrics and category breakdown for UI display.
"""

from typing import Any

from app.models.enums import PolicyStatus
from app.policies.base_policy import PolicyResult


class PolicyReporter:
    """Formats policy compliance telemetry summary."""

    def build_compliance_summary(self, results: list[PolicyResult]) -> dict[str, Any]:
        """Build compliance summary dashboard statistics."""
        passed_cnt = sum(1 for r in results if r.status == PolicyStatus.PASS)
        warning_cnt = sum(1 for r in results if r.status == PolicyStatus.WARNING)
        failed_cnt = sum(1 for r in results if r.status == PolicyStatus.FAIL)
        total = len(results)

        return {
            "total_policies_evaluated": total,
            "passed_count": passed_cnt,
            "warning_count": warning_cnt,
            "failed_count": failed_cnt,
            "compliance_rate_percent": (passed_cnt / total * 100.0) if total > 0 else 100.0,
        }
