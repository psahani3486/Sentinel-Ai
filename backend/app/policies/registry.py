"""
Sentinel AI — Policy Strategy & Specification Registry

Factory & Registry Pattern maintaining instances of enterprise policy rules.
"""

import logging

from app.policies.base_policy import BasePolicy
from app.policies.policies import (
    CatalogGovernancePolicy,
    DatasetGovernancePolicy,
    DriftThresholdPolicy,
    IncidentEscalationPolicy,
    PluginPolicy,
    QualityThresholdPolicy,
    RetentionPolicy,
    SchemaPolicy,
    ValidationPolicy,
    WorkflowPolicy,
)

logger = logging.getLogger(__name__)


class PolicyRegistry:
    """Factory registry maintaining policy Specification strategies."""

    def __init__(self) -> None:
        self._policies: dict[str, BasePolicy] = {}
        self._register_default_policies()

    def _register_default_policies(self) -> None:
        """Register default 10 policy rules."""
        rules = [
            DatasetGovernancePolicy(),
            SchemaPolicy(),
            ValidationPolicy(),
            QualityThresholdPolicy(),
            DriftThresholdPolicy(),
            WorkflowPolicy(),
            PluginPolicy(),
            CatalogGovernancePolicy(),
            RetentionPolicy(),
            IncidentEscalationPolicy(),
        ]
        for r in rules:
            self.register(r)

    def register(self, policy: BasePolicy) -> None:
        """Register a policy rule Specification strategy."""
        self._policies[policy.policy_id] = policy
        logger.debug("Registered Enterprise Policy Rule: %s", policy.policy_name)

    def get(self, policy_id: str) -> BasePolicy | None:
        """Retrieve policy Specification strategy by policy_id."""
        return self._policies.get(policy_id)

    def get_all(self) -> list[BasePolicy]:
        """Return list of all registered policy rules."""
        return list(self._policies.values())


# Global default registry singleton
_default_registry: PolicyRegistry | None = None


def get_policy_registry() -> PolicyRegistry:
    """Return singleton PolicyRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = PolicyRegistry()
    return _default_registry
