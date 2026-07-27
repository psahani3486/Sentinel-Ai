"""
Sentinel AI — Phase 5B Workflow Orchestration Engine Test Suite

Tests WorkflowStateMachine, retry policies, DAG step dependency resolution, all 10 built-in workflows,
WorkflowEngine, WorkflowService, and REST API endpoints.
"""

import uuid
import pytest

from app.models.enums import WorkflowState, WorkflowStepState, WorkflowType
from app.services.workflow_service import WorkflowService
from app.workflows.base_workflow import WorkflowContext, WorkflowStepDefinition
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
from app.workflows.engine import WorkflowEngine
from app.workflows.executor import WorkflowExecutor
from app.workflows.state_machine import InvalidStateTransitionError, WorkflowStateMachine


# ── State Machine Tests ────────────────────────────────────────────────────────
def test_workflow_state_machine_transitions():
    """Test valid and invalid workflow state transitions."""
    sm = WorkflowStateMachine()

    # Valid transition chain: CREATED -> READY -> RUNNING -> COMPLETED
    s = sm.transition(WorkflowState.CREATED, WorkflowState.READY)
    assert s == WorkflowState.READY

    s = sm.transition(s, WorkflowState.RUNNING)
    assert s == WorkflowState.RUNNING

    s = sm.transition(s, WorkflowState.COMPLETED)
    assert s == WorkflowState.COMPLETED

    # Invalid transition: COMPLETED -> RUNNING should raise InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        sm.transition(WorkflowState.COMPLETED, WorkflowState.RUNNING)


# ── Retry Policy & DAG Resolution Tests ───────────────────────────────────────
def test_workflow_executor_retry_and_dependencies():
    """Test step execution with retries and DAG dependency checks."""
    executor = WorkflowExecutor()
    ctx = WorkflowContext(workflow_type=WorkflowType.VALIDATION, dataset_id=uuid.uuid4())

    sdef1 = WorkflowStepDefinition("step1", "TestStep", max_retries=2)
    sout1 = executor.execute_step(sdef1, ctx)
    assert sout1.state == WorkflowStepState.COMPLETED

    # Test unfulfilled dependency -> Should SKIP
    ctx.step_outputs["step1"] = sout1
    sdef2 = WorkflowStepDefinition("step2", "TestStep2", depends_on=["missing_dep"])
    sout2 = executor.execute_step(sdef2, ctx)
    assert sout2.state == WorkflowStepState.SKIPPED


# ── Workflow Strategy Tests ───────────────────────────────────────────────────
def test_all_10_builtin_workflows():
    """Test DAG step definition extraction for all 10 built-in workflows."""
    assert len(DatasetIngestionWorkflow().get_step_definitions()) == 3
    assert len(ValidationWorkflow().get_step_definitions()) == 3
    assert len(ProfilingWorkflow().get_step_definitions()) == 3
    assert len(DriftDetectionWorkflow().get_step_definitions()) == 3
    assert len(AlertWorkflow().get_step_definitions()) == 3
    assert len(IncidentWorkflow().get_step_definitions()) == 3
    assert len(RootCauseWorkflow().get_step_definitions()) == 3
    assert len(RecommendationWorkflow().get_step_definitions()) == 3
    assert len(ForecastWorkflow().get_step_definitions()) == 3
    assert len(EndToEndInvestigationWorkflow().get_step_definitions()) == 9


def test_workflow_engine_end_to_end():
    """Test WorkflowEngine end-to-end DAG execution."""
    engine = WorkflowEngine()
    ctx = WorkflowContext(
        workflow_type=WorkflowType.END_TO_END_INVESTIGATION,
        dataset_id=uuid.uuid4(),
    )
    res = engine.run_workflow(ctx)
    assert res.state == WorkflowState.COMPLETED
    assert len(res.step_outputs) == 9


@pytest.mark.asyncio
async def test_workflow_service_and_rest_api(client, auth_headers, db_session):
    """Test WorkflowService and REST API endpoints /workflows/run, /, /{id}, and /{id}/steps."""
    svc = WorkflowService(db_session)
    ds_id = uuid.uuid4()

    run = await svc.run_workflow(
        workflow_type=WorkflowType.END_TO_END_INVESTIGATION,
        dataset_id=ds_id,
        title="Full Platform E2E Investigation DAG",
    )
    await db_session.commit()
    run_id = str(run.id)

    # 1. Run via POST
    resp_post = await client.post(
        "/api/v1/workflows/run",
        headers=auth_headers,
        json={
            "workflow_type": "validation",
            "dataset_id": str(ds_id),
            "title": "Validation Suite DAG",
        },
    )
    assert resp_post.status_code == 201
    assert resp_post.json()["workflow_type"] == "validation"

    # 2. Get History via GET
    resp_list = await client.get("/api/v1/workflows", headers=auth_headers)
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 2

    # 3. Get Detail via GET
    resp_detail = await client.get(f"/api/v1/workflows/{run_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == run_id

    # 4. Get Steps via GET
    resp_steps = await client.get(f"/api/v1/workflows/{run_id}/steps", headers=auth_headers)
    assert resp_steps.status_code == 200
    assert len(resp_steps.json()) == 9
