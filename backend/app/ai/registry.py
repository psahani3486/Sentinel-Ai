"""
Sentinel AI — Root Cause Analyzer Registry

Registry Pattern mapping AnalysisType enums to concrete analyzer strategy instances.
"""

import logging

from app.ai.analyzers import (
    AlertCorrelationAnalyzer,
    DataDriftAnalyzer,
    JobFailureAnalyzer,
    PipelineFailureAnalyzer,
    QualityDegradationAnalyzer,
    SchemaChangeAnalyzer,
    ValidationFailureAnalyzer,
)
from app.ai.base_analyzer import BaseAnalyzer
from app.models.enums import AnalysisType

logger = logging.getLogger(__name__)


class AnalyzerRegistry:
    """Registry maintaining instances of all automated AI root cause analyzers."""

    def __init__(self) -> None:
        self._analyzers: dict[AnalysisType, BaseAnalyzer] = {}
        self._register_default_analyzers()

    def _register_default_analyzers(self) -> None:
        """Register default 7 root cause analyzers."""
        analyzers = [
            ValidationFailureAnalyzer(),
            DataDriftAnalyzer(),
            SchemaChangeAnalyzer(),
            AlertCorrelationAnalyzer(),
            PipelineFailureAnalyzer(),
            JobFailureAnalyzer(),
            QualityDegradationAnalyzer(),
        ]
        for a in analyzers:
            self.register(a)

    def register(self, analyzer: BaseAnalyzer) -> None:
        """Register an analyzer strategy."""
        self._analyzers[analyzer.analysis_type] = analyzer
        logger.debug("Registered AI Analyzer Strategy: %s", analyzer.analysis_type.value)

    def get(self, analysis_type: AnalysisType) -> BaseAnalyzer:
        """Retrieve analyzer strategy by AnalysisType."""
        analyzer = self._analyzers.get(analysis_type)
        if not analyzer:
            # Fallback to ValidationFailureAnalyzer if unspecified
            return ValidationFailureAnalyzer()
        return analyzer

    def get_all(self) -> list[BaseAnalyzer]:
        """Return list of all registered analyzers."""
        return list(self._analyzers.values())


# Global default registry singleton
_default_registry: AnalyzerRegistry | None = None


def get_analyzer_registry() -> AnalyzerRegistry:
    """Return singleton AnalyzerRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = AnalyzerRegistry()
    return _default_registry
