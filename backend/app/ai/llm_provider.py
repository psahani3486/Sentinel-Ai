"""
Sentinel AI — Pluggable LLM Provider Abstraction

Defines BaseLLMProvider interface, GroqLLMProvider (powered by Groq AI Llama 3 models),
and MockLLMProvider for offline deterministic AI explanation generation.
"""

import abc
import logging
from typing import Any

import httpx

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class BaseLLMProvider(abc.ABC):
    """Abstract interface for LLM explanation providers (Groq, OpenAI, Anthropic, Mock)."""

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


class GroqLLMProvider(BaseLLMProvider):
    """
    High-performance Groq LLM provider using Llama 3 models for real-time
    root cause diagnostics and automated AI recommendations.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def provider_name(self) -> str:
        return f"GroqLLMProvider({self.model})"

    def generate_explanation(self, prompt: str, context_data: dict[str, Any]) -> str:
        if not self.api_key:
            logger.info("GROQ_API_KEY not configured. Falling back to MockLLMProvider.")
            return MockLLMProvider().generate_explanation(prompt, context_data)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an expert Data Observability and Industrial Quality AI Diagnostic Agent for Sentinel AI. "
                            "Generate precise, technical, single-paragraph root cause diagnostics and remediation recommendations."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Prompt: {prompt}\nContext Data: {context_data}",
                    },
                ],
                "max_tokens": 300,
                "temperature": 0.2,
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                explanation = data["choices"][0]["message"]["content"].strip()
                return explanation
        except Exception as e:
            logger.warning("Groq API request failed: %s. Falling back to MockLLMProvider.", str(e))
            return MockLLMProvider().generate_explanation(prompt, context_data)


def get_default_llm_provider() -> BaseLLMProvider:
    """Factory function returning active LLM provider (GroqLLMProvider if key exists, else MockLLMProvider)."""
    settings = get_settings()
    if settings.GROQ_API_KEY:
        return GroqLLMProvider()
    return MockLLMProvider()
