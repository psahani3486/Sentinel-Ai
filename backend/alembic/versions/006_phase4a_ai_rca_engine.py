"""Phase 4A — AI Root Cause Analysis Engine Schema

Revision ID: 006_phase4a_ai_rca_engine
Revises: 005_phase3e_alert_engine
Create Date: 2026-07-26 19:22:00.000000

Creates:
- Enum types: analysis_type, analysis_status, analysis_severity
- Tables: root_cause_analyses, analysis_evidences
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_phase4a_ai_rca_engine"
down_revision: str | None = "005_phase3e_alert_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        analysis_type = postgresql.ENUM(
            "validation_failure", "data_drift", "schema_change",
            "alert_correlation", "pipeline_failure", "job_failure",
            "quality_degradation", name="analysis_type"
        )
        analysis_status = postgresql.ENUM("pending", "completed", "failed", name="analysis_status")
        analysis_severity = postgresql.ENUM("critical", "high", "medium", "low", "info", name="analysis_severity")
        analysis_type.create(bind, checkfirst=True)
        analysis_status.create(bind, checkfirst=True)
        analysis_severity.create(bind, checkfirst=True)

    # 2. Create root_cause_analyses Table
    op.create_table(
        "root_cause_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_type", sa.String(64), nullable=False),
        sa.Column("target_entity_type", sa.String(64), nullable=False),
        sa.Column("target_entity_id", sa.String(255), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("probable_root_cause", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("severity", sa.String(32), nullable=False, server_default="info"),
        sa.Column("affected_components", sa.JSON(), nullable=True),
        sa.Column("recommended_actions", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="completed"),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("llm_provider_name", sa.String(64), nullable=False, server_default="MockLLMProvider"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_root_cause_analyses_target_entity_id", "root_cause_analyses", ["target_entity_id"])
    op.create_index("ix_root_cause_analyses_dataset_id", "root_cause_analyses", ["dataset_id"])
    op.create_index("ix_root_cause_analyses_analysis_type", "root_cause_analyses", ["analysis_type"])
    op.create_index("ix_root_cause_analyses_created_at", "root_cause_analyses", ["created_at"])

    # 3. Create analysis_evidences Table
    op.create_table(
        "analysis_evidences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("root_cause_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_payload", sa.JSON(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_analysis_evidences_analysis_id", "analysis_evidences", ["analysis_id"])
    op.create_index("ix_analysis_evidences_created_at", "analysis_evidences", ["created_at"])


def downgrade() -> None:
    op.drop_table("analysis_evidences")
    op.drop_table("root_cause_analyses")
