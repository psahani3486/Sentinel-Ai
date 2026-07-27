"""Phase 7B — Enterprise Policy Engine & Rule Governance Schema

Revision ID: 014_phase7b_policy_engine
Revises: 013_phase7a_telemetry_engine
Create Date: 2026-07-27 09:18:00.000000

Creates:
- Enum types: policy_category, policy_status, policy_severity
- Tables: policy_definitions, policy_evaluations
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014_phase7b_policy_engine"
down_revision: str | None = "013_phase7a_telemetry_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        policy_category = postgresql.ENUM(
            "dataset_governance", "schema", "validation", "quality_threshold",
            "drift_threshold", "workflow", "plugin", "catalog_governance",
            "retention", "incident_escalation", name="policy_category"
        )
        policy_status = postgresql.ENUM("pass", "fail", "warning", name="policy_status")
        policy_severity = postgresql.ENUM("critical", "high", "medium", "low", "info", name="policy_severity")
        policy_category.create(bind, checkfirst=True)
        policy_status.create(bind, checkfirst=True)
        policy_severity.create(bind, checkfirst=True)

    # 2. Create policy_definitions Table
    op.create_table(
        "policy_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("policy_name", sa.String(255), nullable=False, unique=True),
        sa.Column("category", sa.String(64), nullable=False, server_default="dataset_governance"),
        sa.Column("severity", sa.String(32), nullable=False, server_default="high"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rules_spec", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_policy_definitions_policy_name", "policy_definitions", ["policy_name"], unique=True)
    op.create_index("ix_policy_definitions_category", "policy_definitions", ["category"])
    op.create_index("ix_policy_definitions_severity", "policy_definitions", ["severity"])
    op.create_index("ix_policy_definitions_is_active", "policy_definitions", ["is_active"])
    op.create_index("ix_policy_definitions_created_at", "policy_definitions", ["created_at"])

    # 3. Create policy_evaluations Table
    op.create_table(
        "policy_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policy_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pass"),
        sa.Column("severity", sa.String(32), nullable=False, server_default="high"),
        sa.Column("evidence", sa.JSON(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_policy_evaluations_policy_id", "policy_evaluations", ["policy_id"])
    op.create_index("ix_policy_evaluations_status", "policy_evaluations", ["status"])
    op.create_index("ix_policy_evaluations_severity", "policy_evaluations", ["severity"])
    op.create_index("ix_policy_evaluations_evaluated_at", "policy_evaluations", ["evaluated_at"])
    op.create_index("ix_policy_evaluations_created_at", "policy_evaluations", ["created_at"])


def downgrade() -> None:
    op.drop_table("policy_evaluations")
    op.drop_table("policy_definitions")
