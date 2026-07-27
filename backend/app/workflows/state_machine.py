"""
Sentinel AI — Workflow State Machine

Validates state transitions for workflow execution runs.
States: CREATED, READY, RUNNING, WAITING, COMPLETED, FAILED, CANCELLED, SKIPPED.
"""

from app.models.enums import WorkflowState


class InvalidStateTransitionError(ValueError):
    """Exception raised when an invalid workflow state transition is attempted."""

    pass


class WorkflowStateMachine:
    """Manages valid state transitions for workflow runs."""

    ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
        WorkflowState.CREATED: {WorkflowState.READY, WorkflowState.CANCELLED},
        WorkflowState.READY: {WorkflowState.RUNNING, WorkflowState.CANCELLED, WorkflowState.SKIPPED},
        WorkflowState.RUNNING: {
            WorkflowState.WAITING,
            WorkflowState.COMPLETED,
            WorkflowState.FAILED,
            WorkflowState.CANCELLED,
        },
        WorkflowState.WAITING: {WorkflowState.RUNNING, WorkflowState.CANCELLED, WorkflowState.FAILED},
        WorkflowState.COMPLETED: set(),
        WorkflowState.FAILED: {WorkflowState.READY},  # Allows restart
        WorkflowState.CANCELLED: set(),
        WorkflowState.SKIPPED: set(),
    }

    def transition(self, current: WorkflowState, target: WorkflowState) -> WorkflowState:
        """
        Validate and perform state transition from current state to target state.

        Args:
            current: Current WorkflowState.
            target: Proposed target WorkflowState.

        Returns:
            Validated target WorkflowState.

        Raises:
            InvalidStateTransitionError if transition is invalid.
        """
        if current == target:
            return target

        allowed = self.ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition Workflow from '{current.value}' to '{target.value}'."
            )
        return target
