"""Phase 4B — AI Recommendation Engine Schema

Revision ID: 007_phase4b_recommendation_engine
Revises: 006_phase4a_ai_rca_engine
Create Date: 2026-07-26 19:32:00.000000

Creates:
- Enum types: recommendation_priority, recommendation_category
- Tables: recommendations, recommendation_evidences
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007_phase4b_recommendation_engine"
down_revision: str | None = "006_phase4a_ai_rca_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        recommendation_priority = postgresql.ENUM("critical", "high", "medium", "low", "info", name="recommendation_priority")
        recommendation_category = postgresql.ENUM(
            "validation_failure", "schema_change", "data_drift",
            "pipeline_failure", "connector_failure", "job_failure",
            "quality_score_drop", "alert_correlation", "missing_values",
            "outlier_detection", name="recommendation_category"
        )
        recommendation_priority.create(bind, checkfirst=True)
        recommendation_category.create(bind, checkfirst=True)

    # 2. Create recommendations Table
    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("rca_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("root_cause_analyses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("priority", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("estimated_impact", sa.String(32), nullable=False, server_default="HIGH"),
        sa.Column("estimated_effort", sa.String(32), nullable=False, server_default="LOW"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("priority_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("suggested_next_steps", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_recommendations_rca_id", "recommendations", ["rca_id"])
    op.create_index("ix_recommendations_dataset_id", "recommendations", ["dataset_id"])
    op.create_index("ix_recommendations_category", "recommendations", ["category"])
    op.create_index("ix_recommendations_priority", "recommendations", ["priority"])
    op.create_index("ix_recommendations_priority_score", "recommendations", ["priority_score"])
    op.create_index("ix_recommendations_created_at", "recommendations", ["created_at"])

    # 3. Create recommendation_evidences Table
    op.create_table(
        "recommendation_evidences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_payload", sa.JSON(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_recommendation_evidences_recommendation_id", "recommendation_evidences", ["recommendation_id"])
    op.create_index("ix_recommendation_evidences_created_at", "recommendation_evidences", ["created_at"])


def downgrade() -> None:
    op.drop_table("recommendation_evidences")
    op.drop_table("recommendations")
