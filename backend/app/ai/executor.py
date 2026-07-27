"""
Sentinel AI — Analysis Executor

Executes target diagnostic analyzers against telemetry context.
"""

from app.ai.base_analyzer import AnalysisContext, RawDiagnosticResult
from app.ai.registry import AnalyzerRegistry, get_analyzer_registry


class AnalysisExecutor:
    """Executes target analyzer strategy for a given AnalysisContext."""

    def __init__(self, registry: AnalyzerRegistry | None = None) -> None:
        self._registry = registry or get_analyzer_registry()

    def execute_analysis(self, context: AnalysisContext) -> RawDiagnosticResult:
        """
        Execute target analyzer matching context.analysis_type.

        Returns:
            RawDiagnosticResult containing findings and evidence candidates.
        """
        analyzer = self._registry.get(context.analysis_type)
        return analyzer.analyze(context)
