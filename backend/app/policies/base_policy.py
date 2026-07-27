"""
Sentinel AI — Base Policy & Specification Pattern Interfaces

Defines BasePolicy Specification Pattern abstract strategy interface and PolicyResult dataclass.
"""

import abc
import datetime
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import PolicyCategory, PolicySeverity, PolicyStatus


@dataclass
class PolicyResult:
    """Dataclass holding policy evaluation outcome."""

    policy_id: str
    policy_name: str
    category: PolicyCategory
    status: PolicyStatus
    severity: PolicySeverity
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendation: str = "No action required."
    evaluated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


class BasePolicy(abc.ABC):
    """
    Abstract Specification Pattern interface implemented by all enterprise policies.
    """

    @property
    @abc.abstractmethod
    def policy_id(self) -> str:
        """Return unique policy identifier string."""
        pass

    @property
    @abc.abstractmethod
    def policy_name(self) -> str:
        """Return human-readable policy name."""
        pass

    @property
    @abc.abstractmethod
    def category(self) -> PolicyCategory:
        """Return policy category."""
        pass

    @property
    @abc.abstractmethod
    def severity(self) -> PolicySeverity:
        """Return policy severity level."""
        pass

    @abc.abstractmethod
    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        """
        Specification Pattern method returning True if target satisfies rule constraints.
        """
        pass

    @abc.abstractmethod
    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        """Evaluate target payload and return PolicyResult."""
        pass
