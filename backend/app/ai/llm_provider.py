"""
Sentinel AI — Pluggable LLM Provider Abstraction

Defines BaseLLMProvider interface and MockLLMProvider implementation for offline
deterministic AI explanation generation.
"""

import abc
from typing import Any


class BaseLLMProvider(abc.ABC):
    """Abstract interface for LLM explanation providers (OpenAI, Anthropic, Bedrock, Mock)."""

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier name."""
        pass

    @abc.abstractmethod
    def generate_explanation(self, prompt: str, context_data: dict[str, Any]) -> str:
        """
        Generate natural language diagnostic explanation for an RCA event.

        Args:
            prompt: Structured prompt string.
            context_data: Diagnostic telemetry context dictionary.

        Returns:
            Generated explanation string.
        """
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider generating deterministic diagnostic explanations from rule evidence
    without calling external APIs.
    """

    @property
    def provider_name(self) -> str:
        return "MockLLMProvider"

    def generate_explanation(self, prompt: str, context_data: dict[str, Any]) -> str:
        analysis_type = context_data.get("analysis_type", "incident")
        target_id = context_data.get("target_id", "unknown")
        failed_count = context_data.get("failed_rules_count", 0)
        drift_score = context_data.get("drift_score", 0.0)

        if analysis_type == "validation_failure":
            return (
                f"Automated AI Diagnostic: Validation suite '{target_id}' failed due to {failed_count} rule violations. "
                "The primary anomaly stems from unexpected null values and out-of-range sensor readings in primary ingest columns. "
                "Upstream ingestion connectors should verify upstream data schema constraints."
            )
        elif analysis_type == "data_drift":
            return (
                f"Automated AI Diagnostic: Dataset '{target_id}' experienced significant distribution shift (PSI score {drift_score:.2f}). "
                "Quantile divergence indicates a statistical mean shift in numerical features following recent ETL batch ingestion."
            )
        elif analysis_type == "schema_change":
            return (
                f"Automated AI Diagnostic: Schema evolution detected on '{target_id}'. "
                "Columns were modified or renamed, breaking downstream type assertion contracts."
            )
        else:
            return (
                f"Automated AI Diagnostic: Diagnostic analysis for '{target_id}' identified correlated platform anomalies. "
                "Review raw execution telemetry and retry failed worker tasks."
            )
