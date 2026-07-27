"""
Sentinel AI — Base Recommendation Strategy Interface

Defines BaseRecommendationStrategy abstract strategy interface, RecommendationContext,
EvidenceItem, and RawRecommendationCandidate dataclasses.
"""

import abc
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import RecommendationCategory, RecommendationPriority


@dataclass
class EvidenceItem:
    """Dataclass representing supporting evidence attached to a recommendation."""

    title: str
    description: str
    evidence_payload: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0


@dataclass
class RecommendationContext:
    """Telemetry context container supplied to recommendation strategies."""

    category: RecommendationCategory
    rca_id: uuid.UUID | None = None
    dataset_id: uuid.UUID | None = None
    rca_summary: str | None = None
    rca_probable_root_cause: str | None = None
    rca_affected_components: list[str] = field(default_factory=list)
    telemetry_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class RawRecommendationCandidate:
    """Raw recommendation candidate output produced by a strategy before prioritization scoring."""

    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    description: str
    estimated_impact: str  # HIGH, MEDIUM, LOW
    estimated_effort: str  # LOW, MEDIUM, HIGH
    confidence_score: float
    suggested_next_steps: list[str] = field(default_factory=list)
    evidences: list[EvidenceItem] = field(default_factory=list)


class BaseRecommendationStrategy(abc.ABC):
    """Abstract strategy interface for automated AI remediation recommendation rules."""

    @property
    @abc.abstractmethod
    def category(self) -> RecommendationCategory:
        """Return the unique RecommendationCategory enum key."""
        pass

    @abc.abstractmethod
    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        """
        Generate remediation recommendation candidate from telemetry context.

        Args:
            context: RecommendationContext containing RCA and platform telemetry.

        Returns:
            RawRecommendationCandidate containing actionable remediation advice.
        """
        pass
