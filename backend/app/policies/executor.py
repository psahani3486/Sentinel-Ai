"""
Sentinel AI — Policy Executor

Executes policy Specification rules against target payloads and produces PolicyResult items.
"""

from typing import Any

from app.policies.base_policy import PolicyResult
from app.policies.registry import PolicyRegistry, get_policy_registry


class PolicyExecutor:
    """Executes policy Specification rules against target payloads."""

    def __init__(self, registry: PolicyRegistry | None = None) -> None:
        self._registry = registry or get_policy_registry()

    def evaluate_all(self, target: dict[str, Any] | None = None) -> list[PolicyResult]:
        """Evaluate target payload against all registered policies."""
        payload = target or {}
        results = []
        for p in self._registry.get_all():
            results.append(p.evaluate(payload))
        return results
