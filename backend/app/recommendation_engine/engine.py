"""
Sentinel AI — Recommendation Engine

Calculates weighted priority scores, applies LLM explanation enhancement,
and outputs ranked remediation recommendations.
"""

import time
from dataclasses import dataclass, field

from app.ai.llm_provider import BaseLLMProvider, MockLLMProvider
from app.models.enums import RecommendationCategory, RecommendationPriority
from app.recommendation_engine.base_strategy import EvidenceItem, RecommendationContext
from app.recommendation_engine.executor import RecommendationExecutor


def calculate_priority_score(
    priority: RecommendationPriority,
    estimated_impact: str,
    estimated_effort: str,
    confidence_score: float,
) -> float:
    """
    Prioritization ranking formula:
    Priority Score = (Severity * 0.35) + (Impact * 0.30) + (Confidence * 0.20) + (EaseOfEffort * 0.15)
    """
    severity_map = {
        RecommendationPriority.CRITICAL: 100.0,
        RecommendationPriority.HIGH: 80.0,
        RecommendationPriority.MEDIUM: 50.0,
        RecommendationPriority.LOW: 30.0,
        RecommendationPriority.INFO: 10.0,
    }
    impact_map = {"HIGH": 100.0, "MEDIUM": 60.0, "LOW": 30.0}
    effort_ease_map = {"LOW": 100.0, "MEDIUM": 60.0, "HIGH": 30.0}

    sev_w = severity_map.get(priority, 50.0)
    imp_w = impact_map.get(estimated_impact.upper(), 60.0)
    eff_w = effort_ease_map.get(estimated_effort.upper(), 60.0)

    score = (sev_w * 0.35) + (imp_w * 0.30) + (confidence_score * 0.20) + (eff_w * 0.15)
    return round(score, 1)


@dataclass
class ProcessedRecommendationResult:
    """Dataclass representing output produced by RecommendationEngine."""

    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    description: str
    estimated_impact: str
    estimated_effort: str
    confidence_score: float
    priority_score: float
    suggested_next_steps: list[str] = field(default_factory=list)
    evidences: list[EvidenceItem] = field(default_factory=list)
    execution_time_ms: float = 0.0


class RecommendationEngine:
    """Coordinates recommendation strategy execution, priority scoring, and LLM enhancement."""

    def __init__(
        self,
        executor: RecommendationExecutor | None = None,
        llm_provider: BaseLLMProvider | None = None,
    ) -> None:
        self._executor = executor or RecommendationExecutor()
        self._llm_provider = llm_provider or MockLLMProvider()

    def generate_recommendation(
        self, context: RecommendationContext
    ) -> ProcessedRecommendationResult:
        """
        Execute 2-phase recommendation pipeline:
        1. Deterministic strategy evaluation + weighted priority score calculation.
        2. LLM explanation enhancement.
        """
        start_time = time.perf_counter()

        # Phase 1: Strategy Execution
        raw = self._executor.execute_strategy(context)

        # Calculate Prioritization Score
        score = calculate_priority_score(
            raw.priority, raw.estimated_impact, raw.estimated_effort, raw.confidence_score
        )

        # Phase 2: LLM Enhancement
        prompt = f"Enhance remediation advice for {context.category.value}."
        llm_context = {
            "analysis_type": context.category.value,
            "target_id": str(context.dataset_id or "asset"),
        }
        llm_enhancement = self._llm_provider.generate_explanation(prompt, llm_context)

        exec_ms = (time.perf_counter() - start_time) * 1000.0

        enhanced_desc = f"{raw.description}\n\nAI Insight: {llm_enhancement}"

        return ProcessedRecommendationResult(
            category=raw.category,
            priority=raw.priority,
            title=raw.title,
            description=enhanced_desc,
            estimated_impact=raw.estimated_impact,
            estimated_effort=raw.estimated_effort,
            confidence_score=raw.confidence_score,
            priority_score=score,
            suggested_next_steps=raw.suggested_next_steps,
            evidences=raw.evidences,
            execution_time_ms=exec_ms,
        )
