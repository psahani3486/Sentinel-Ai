"""
Sentinel AI — Workflow Strategy Registry

Registry Pattern mapping WorkflowType enums to concrete workflow instances.
"""

import logging

from app.models.enums import WorkflowType
from app.workflows.base_workflow import BaseWorkflow
from app.workflows.builtins import (
    AlertWorkflow,
    DatasetIngestionWorkflow,
    DriftDetectionWorkflow,
    EndToEndInvestigationWorkflow,
    ForecastWorkflow,
    IncidentWorkflow,
    ProfilingWorkflow,
    RecommendationWorkflow,
    RootCauseWorkflow,
    ValidationWorkflow,
)

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """Registry maintaining instances of all built-in Sentinel AI workflows."""

    def __init__(self) -> None:
        self._workflows: dict[WorkflowType, BaseWorkflow] = {}
        self._register_default_workflows()

    def _register_default_workflows(self) -> None:
        """Register default 10 built-in workflows."""
        workflows = [
            DatasetIngestionWorkflow(),
            ValidationWorkflow(),
            ProfilingWorkflow(),
            DriftDetectionWorkflow(),
            AlertWorkflow(),
            IncidentWorkflow(),
            RootCauseWorkflow(),
            RecommendationWorkflow(),
            ForecastWorkflow(),
            EndToEndInvestigationWorkflow(),
        ]
        for w in workflows:
            self.register(w)

    def register(self, workflow: BaseWorkflow) -> None:
        """Register a workflow strategy."""
        self._workflows[workflow.workflow_type] = workflow
        logger.debug("Registered Workflow Strategy: %s", workflow.workflow_type.value)

    def get(self, workflow_type: WorkflowType) -> BaseWorkflow:
        """Retrieve workflow strategy by WorkflowType."""
        wf = self._workflows.get(workflow_type)
        if not wf:
            return EndToEndInvestigationWorkflow()
        return wf

    def get_all(self) -> list[BaseWorkflow]:
        """Return list of all registered workflows."""
        return list(self._workflows.values())


# Global default registry singleton
_default_registry: WorkflowRegistry | None = None


def get_workflow_registry() -> WorkflowRegistry:
    """Return singleton WorkflowRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = WorkflowRegistry()
    return _default_registry
