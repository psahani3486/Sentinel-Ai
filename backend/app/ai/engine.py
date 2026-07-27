"""
Sentinel AI — Root Cause Engine

Coordinates deterministic rule-based telemetry analysis and LLM explanation synthesis.
"""

import time
from dataclasses import dataclass, field

from app.ai.base_analyzer import AnalysisContext, EvidenceCandidate
from app.ai.executor import AnalysisExecutor
from app.ai.llm_provider import BaseLLMProvider, MockLLMProvider
from app.models.enums import ValidationSeverity


@dataclass
class StructuredRCAReport:
    """Structured result produced by RootCauseEngine."""

    summary: str
    probable_root_cause: str
    confidence_score: float
    severity: ValidationSeverity
    affected_components: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    evidences: list[EvidenceCandidate] = field(default_factory=list)
    execution_time_ms: float = 0.0
    llm_provider_name: str = "MockLLMProvider"


class RootCauseEngine:
    """Hybrid AI Engine combining deterministic rule analysis with LLM explanation generation."""

    def __init__(
        self,
        executor: AnalysisExecutor | None = None,
        llm_provider: BaseLLMProvider | None = None,
    ) -> None:
        self._executor = executor or AnalysisExecutor()
        self._llm_provider = llm_provider or MockLLMProvider()

    def run_root_cause_analysis(self, context: AnalysisContext) -> StructuredRCAReport:
        """
        Execute hybrid 2-phase RCA pipeline:
        1. Deterministic rule-based statistical pattern matching & evidence extraction.
        2. LLM explanation synthesis layer.
        """
        start_time = time.perf_counter()

        # Phase 1: Deterministic Rule Analysis
        raw_result = self._executor.execute_analysis(context)

        # Phase 2: LLM Explanation Synthesis
        llm_prompt = f"Analyze root cause for {context.analysis_type.value} on entity {context.target_entity_id}."
        llm_context = {
            "analysis_type": context.analysis_type.value,
            "target_id": context.target_entity_id,
            "failed_rules_count": len(context.validation_results),
            "summary": raw_result.summary,
        }
        llm_explanation = self._llm_provider.generate_explanation(llm_prompt, llm_context)

        exec_ms = (time.perf_counter() - start_time) * 1000.0

        # Enhance summary with LLM synthesis
        combined_summary = f"{raw_result.summary}\n\n{llm_explanation}"

        return StructuredRCAReport(
            summary=combined_summary,
            probable_root_cause=raw_result.probable_root_cause,
            confidence_score=raw_result.confidence_score,
            severity=raw_result.severity,
            affected_components=raw_result.affected_components,
            recommended_actions=raw_result.recommended_actions,
            evidences=raw_result.evidences,
            execution_time_ms=exec_ms,
            llm_provider_name=self._llm_provider.provider_name,
        )
