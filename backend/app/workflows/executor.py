"""
Sentinel AI — Workflow Executor

Executes DAG steps according to dependency constraints and retry policies.
"""

import time
from typing import Any

from app.models.enums import WorkflowStepState
from app.workflows.base_workflow import (
    WorkflowContext,
    WorkflowStepDefinition,
    WorkflowStepOutput,
)


class WorkflowExecutor:
    """Executes workflow step definitions resolving DAG dependencies and retries."""

    def execute_step(
        self,
        step_def: WorkflowStepDefinition,
        context: WorkflowContext,
    ) -> WorkflowStepOutput:
        """
        Execute an individual step definition with retry logic.
        """
        start_time = time.perf_counter()

        # Verify dependencies
        for dep in step_def.depends_on:
            dep_output = context.step_outputs.get(dep)
            if not dep_output or dep_output.state != WorkflowStepState.COMPLETED:
                exec_ms = (time.perf_counter() - start_time) * 1000.0
                return WorkflowStepOutput(
                    step_name=step_def.step_name,
                    state=WorkflowStepState.SKIPPED,
                    execution_time_ms=exec_ms,
                    logs=f"Step skipped due to unfulfilled dependency '{dep}'.",
                )

        # Retry Loop
        attempt = 0
        last_error: str | None = None
        logs = []

        while attempt <= step_def.max_retries:
            attempt += 1
            logs.append(f"Executing step '{step_def.step_name}' (Attempt {attempt}/{step_def.max_retries + 1})...")

            try:
                # Simulated step execution
                outputs: dict[str, Any] = {
                    "status": "success",
                    "step_name": step_def.step_name,
                    "step_type": step_def.step_type,
                    "dataset_id": str(context.dataset_id) if context.dataset_id else None,
                }

                exec_ms = (time.perf_counter() - start_time) * 1000.0
                logs.append(f"Step '{step_def.step_name}' completed successfully in {exec_ms:.1f}ms.")

                return WorkflowStepOutput(
                    step_name=step_def.step_name,
                    state=WorkflowStepState.COMPLETED,
                    execution_time_ms=exec_ms,
                    logs="\n".join(logs),
                    outputs=outputs,
                )
            except Exception as err:
                last_error = str(err)
                logs.append(f"Attempt {attempt} failed: {last_error}")

        exec_ms = (time.perf_counter() - start_time) * 1000.0
        return WorkflowStepOutput(
            step_name=step_def.step_name,
            state=WorkflowStepState.FAILED,
            execution_time_ms=exec_ms,
            logs="\n".join(logs),
            outputs={"error": last_error or "Maximum retries exceeded"},
        )
