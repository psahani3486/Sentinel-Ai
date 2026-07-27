"""Phase 5A — Unified Incident Investigation Workspace Schema

Revision ID: 009_phase5a_incident_workspace
Revises: 008_phase4c_forecasting_engine
Create Date: 2026-07-26 19:55:00.000000

Creates:
- Enum types: incident_status, incident_severity, incident_event_type
- Tables: incidents, incident_events
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "009_phase5a_incident_workspace"
down_revision: str | None = "008_phase4c_forecasting_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        incident_status = postgresql.ENUM("open", "investigating", "mitigated", "resolved", "closed", name="incident_status")
        incident_severity = postgresql.ENUM("critical", "high", "medium", "low", "info", name="incident_severity")
        incident_event_type = postgresql.ENUM(
            "validation_failed", "drift_detected", "schema_changed",
            "alert_triggered", "rca_completed", "recommendation_generated",
            "forecast_alert", "job_failed", name="incident_event_type"
        )
        incident_status.create(bind, checkfirst=True)
        incident_severity.create(bind, checkfirst=True)
        incident_event_type.create(bind, checkfirst=True)

    # 2. Create incidents Table
    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rca_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("root_cause_analyses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("forecast_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("forecast_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False, server_default="high"),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("root_cause_summary", sa.Text(), nullable=True),
        sa.Column("recommendations_summary", sa.Text(), nullable=True),
        sa.Column("forecast_summary", sa.Text(), nullable=True),
        sa.Column("related_datasets", sa.JSON(), nullable=True),
        sa.Column("related_jobs", sa.JSON(), nullable=True),
        sa.Column("related_alerts", sa.JSON(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_incidents_dataset_id", "incidents", ["dataset_id"])
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_severity", "incidents", ["severity"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])

    # 3. Create incident_events Table
    op.create_table(
        "incident_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_link", sa.String(512), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_incident_events_incident_id", "incident_events", ["incident_id"])
    op.create_index("ix_incident_events_timestamp", "incident_events", ["timestamp"])
    op.create_index("ix_incident_events_created_at", "incident_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("incident_events")
    op.drop_table("incidents")
