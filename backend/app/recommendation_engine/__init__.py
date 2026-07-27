"""Recommendation Engine Package."""

from app.recommendation_engine.base_strategy import (
    BaseRecommendationStrategy,
    EvidenceItem,
    RawRecommendationCandidate,
    RecommendationContext,
)
from app.recommendation_engine.engine import (
    ProcessedRecommendationResult,
    RecommendationEngine,
    calculate_priority_score,
)
from app.recommendation_engine.executor import RecommendationExecutor
from app.recommendation_engine.registry import (
    RecommendationRegistry,
    get_recommendation_registry,
)
from app.recommendation_engine.reporter import RecommendationReporter
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

__all__ = [
    "BaseRecommendationStrategy",
    "RecommendationContext",
    "RawRecommendationCandidate",
    "EvidenceItem",
    "RecommendationRegistry",
    "get_recommendation_registry",
    "RecommendationExecutor",
    "RecommendationEngine",
    "ProcessedRecommendationResult",
    "calculate_priority_score",
    "RecommendationReporter",
    "ValidationFailureRecommendationStrategy",
    "SchemaChangeRecommendationStrategy",
    "DataDriftRecommendationStrategy",
    "PipelineFailureRecommendationStrategy",
    "ConnectorFailureRecommendationStrategy",
    "JobFailureRecommendationStrategy",
    "QualityScoreDropRecommendationStrategy",
    "AlertCorrelationRecommendationStrategy",
    "MissingValuesRecommendationStrategy",
    "OutlierDetectionRecommendationStrategy",
]
