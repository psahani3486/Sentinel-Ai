"""
Sentinel AI — Workflow Reporter

Formats DAG topologies and step logs for UI rendering.
"""

from typing import Any


class WorkflowReporter:
    """Formats workflow executions for UI dashboard and DAG visualization."""

    def build_dashboard_summary(self, workflow_runs: list[Any]) -> dict[str, Any]:
        """Build workflow execution telemetry summary."""
        running_count = 0
        failed_count = 0
        total = len(workflow_runs)

        for run in workflow_runs:
            st = str(getattr(run, "state", "created")).lower()
            if st == "running":
                running_count += 1
            elif st == "failed":
                failed_count += 1

        return {
            "total_workflow_runs": total,
            "running_workflows_count": running_count,
            "failed_workflows_count": failed_count,
            "latest_run": workflow_runs[0] if workflow_runs else None,
        }
