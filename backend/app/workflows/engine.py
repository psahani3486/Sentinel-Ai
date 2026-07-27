"""
Sentinel AI — Workflow Engine

Orchestrates workflow state transitions via WorkflowStateMachine and executes DAG steps.
"""

from app.models.enums import WorkflowState, WorkflowStepState
from app.workflows.base_workflow import RawWorkflowCandidate, WorkflowContext
from app.workflows.executor import WorkflowExecutor
from app.workflows.registry import WorkflowRegistry, get_workflow_registry
from app.workflows.state_machine import WorkflowStateMachine


class WorkflowEngine:
    """Orchestrates workflow state transitions and step DAG execution."""

    def __init__(
        self,
        registry: WorkflowRegistry | None = None,
        executor: WorkflowExecutor | None = None,
        state_machine: WorkflowStateMachine | None = None,
    ) -> None:
        self._registry = registry or get_workflow_registry()
        self._executor = executor or WorkflowExecutor()
        self._state_machine = state_machine or WorkflowStateMachine()

    def run_workflow(self, context: WorkflowContext) -> RawWorkflowCandidate:
        """
        Execute full workflow DAG with state transitions.
        """
        # State transition: CREATED -> READY -> RUNNING
        state = self._state_machine.transition(WorkflowState.CREATED, WorkflowState.READY)
        state = self._state_machine.transition(state, WorkflowState.RUNNING)

        wf_strategy = self._registry.get(context.workflow_type)
        step_defs = wf_strategy.get_step_definitions()

        step_outputs = []
        has_failure = False

        for sdef in step_defs:
            out = self._executor.execute_step(sdef, context)
            context.step_outputs[sdef.step_name] = out
            step_outputs.append(out)

            if out.state == WorkflowStepState.FAILED:
                has_failure = True

        final_state = WorkflowState.FAILED if has_failure else WorkflowState.COMPLETED
        state = self._state_machine.transition(state, final_state)

        return RawWorkflowCandidate(
            workflow_type=context.workflow_type,
            title=context.title,
            state=state,
            step_definitions=step_defs,
            step_outputs=step_outputs,
        )
