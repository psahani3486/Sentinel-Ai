"""Phase 5B — Enterprise Workflow Orchestration Schema

Revision ID: 010_phase5b_workflow_engine
Revises: 009_phase5a_incident_workspace
Create Date: 2026-07-26 20:01:00.000000

Creates:
- Enum types: workflow_state, workflow_step_state, workflow_type
- Tables: workflow_runs, workflow_step_runs
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010_phase5b_workflow_engine"
down_revision: str | None = "009_phase5a_incident_workspace"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        workflow_state = postgresql.ENUM(
            "created", "ready", "running", "waiting",
            "completed", "failed", "cancelled", "skipped", name="workflow_state"
        )
        workflow_step_state = postgresql.ENUM(
            "pending", "running", "completed", "failed", "skipped", "retrying", name="workflow_step_state"
        )
        workflow_type = postgresql.ENUM(
            "dataset_ingestion", "validation", "profiling", "drift_detection",
            "alert", "incident", "root_cause", "recommendation", "forecast",
            "end_to_end_investigation", name="workflow_type"
        )
        workflow_state.create(bind, checkfirst=True)
        workflow_step_state.create(bind, checkfirst=True)
        workflow_type.create(bind, checkfirst=True)

    # 2. Create workflow_runs Table
    op.create_table(
        "workflow_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("workflow_type", sa.String(64), nullable=False),
        sa.Column("state", sa.String(32), nullable=False, server_default="created"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("total_steps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_steps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_steps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("context_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_workflow_runs_dataset_id", "workflow_runs", ["dataset_id"])
    op.create_index("ix_workflow_runs_workflow_type", "workflow_runs", ["workflow_type"])
    op.create_index("ix_workflow_runs_state", "workflow_runs", ["state"])
    op.create_index("ix_workflow_runs_created_at", "workflow_runs", ["created_at"])

    # 3. Create workflow_step_runs Table
    op.create_table(
        "workflow_step_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_name", sa.String(128), nullable=False),
        sa.Column("step_type", sa.String(64), nullable=False),
        sa.Column("state", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("depends_on", sa.JSON(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("logs", sa.Text(), nullable=True),
        sa.Column("outputs", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_workflow_step_runs_workflow_run_id", "workflow_step_runs", ["workflow_run_id"])
    op.create_index("ix_workflow_step_runs_state", "workflow_step_runs", ["state"])
    op.create_index("ix_workflow_step_runs_created_at", "workflow_step_runs", ["created_at"])


def downgrade() -> None:
    op.drop_table("workflow_step_runs")
    op.drop_table("workflow_runs")
