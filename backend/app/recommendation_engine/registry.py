"""
Sentinel AI — Recommendation Strategy Registry

Registry Pattern mapping RecommendationCategory enums to concrete strategy instances.
"""

import logging

from app.models.enums import RecommendationCategory
from app.recommendation_engine.base_strategy import BaseRecommendationStrategy
from app.recommendation_engine.strategies import (
    AlertCorrelationRecommendationStrategy,
    ConnectorFailureRecommendationStrategy,
    DataDriftRecommendationStrategy,
    JobFailureRecommendationStrategy,
    MissingValuesRecommendationStrategy,
    OutlierDetectionRecommendationStrategy,
    PipelineFailureRecommendationStrategy,
    QualityScoreDropRecommendationStrategy,
    SchemaChangeRecommendationStrategy,
    ValidationFailureRecommendationStrategy,
)

logger = logging.getLogger(__name__)


class RecommendationRegistry:
    """Registry maintaining instances of all automated remediation recommendation strategies."""

    def __init__(self) -> None:
        self._strategies: dict[RecommendationCategory, BaseRecommendationStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default 10 recommendation strategies."""
        strategies = [
            ValidationFailureRecommendationStrategy(),
            SchemaChangeRecommendationStrategy(),
            DataDriftRecommendationStrategy(),
            PipelineFailureRecommendationStrategy(),
            ConnectorFailureRecommendationStrategy(),
            JobFailureRecommendationStrategy(),
            QualityScoreDropRecommendationStrategy(),
            AlertCorrelationRecommendationStrategy(),
            MissingValuesRecommendationStrategy(),
            OutlierDetectionRecommendationStrategy(),
        ]
        for s in strategies:
            self.register(s)

    def register(self, strategy: BaseRecommendationStrategy) -> None:
        """Register a recommendation strategy."""
        self._strategies[strategy.category] = strategy
        logger.debug("Registered Recommendation Strategy: %s", strategy.category.value)

    def get(self, category: RecommendationCategory) -> BaseRecommendationStrategy:
        """Retrieve strategy by RecommendationCategory."""
        strat = self._strategies.get(category)
        if not strat:
            return ValidationFailureRecommendationStrategy()
        return strat

    def get_all(self) -> list[BaseRecommendationStrategy]:
        """Return list of all registered strategies."""
        return list(self._strategies.values())


# Global default registry singleton
_default_registry: RecommendationRegistry | None = None


def get_recommendation_registry() -> RecommendationRegistry:
    """Return singleton RecommendationRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = RecommendationRegistry()
    return _default_registry
