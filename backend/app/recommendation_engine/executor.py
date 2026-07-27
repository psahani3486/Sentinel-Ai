"""
Sentinel AI — Recommendation Executor

Executes matching recommendation strategies against supplied telemetry context.
"""

from app.recommendation_engine.base_strategy import RawRecommendationCandidate, RecommendationContext
from app.recommendation_engine.registry import RecommendationRegistry, get_recommendation_registry


class RecommendationExecutor:
    """Executes matching recommendation strategy for a given RecommendationContext."""

    def __init__(self, registry: RecommendationRegistry | None = None) -> None:
        self._registry = registry or get_recommendation_registry()

    def execute_strategy(self, context: RecommendationContext) -> RawRecommendationCandidate:
        """
        Execute strategy matching context.category.

        Returns:
            RawRecommendationCandidate.
        """
        strategy = self._registry.get(context.category)
        return strategy.generate(context)
