"""
Sentinel AI — Policy Engine

Orchestrates policy suite execution, compliance scoring, and policy rule management.
"""

from typing import Any

from app.policies.base_policy import PolicyResult
from app.policies.executor import PolicyExecutor
from app.policies.registry import PolicyRegistry, get_policy_registry


class PolicyEngine:
    """Orchestrates enterprise policy evaluations."""

    def __init__(
        self,
        registry: PolicyRegistry | None = None,
        executor: PolicyExecutor | None = None,
    ) -> None:
        self._registry = registry or get_policy_registry()
        self._executor = executor or PolicyExecutor()

    def evaluate_suite(self, target: dict[str, Any] | None = None) -> list[PolicyResult]:
        """Evaluate target payload across all policy Specification rules."""
        return self._executor.evaluate_all(target)
