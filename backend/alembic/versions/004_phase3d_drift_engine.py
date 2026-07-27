"""Phase 3D — Data Drift Engine Schema

Revision ID: 004_phase3d_drift_engine
Revises: 003_phase3a_background_jobs
Create Date: 2026-07-26 19:10:00.000000

Creates:
- Enum types: drift_status, drift_severity, detector_type
- Tables: drift_runs, drift_results
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_phase3d_drift_engine"
down_revision: str | None = "003_phase3a_background_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        drift_status = postgresql.ENUM("no_drift", "low", "medium", "high", "critical", name="drift_status")
        drift_severity = postgresql.ENUM("critical", "high", "medium", "low", "info", name="drift_severity")
        detector_type = postgresql.ENUM(
            "psi", "jensen_shannon", "kl_divergence", "wasserstein", "mean_drift",
            "std_drift", "missing_value_drift", "cardinality_drift",
            "category_distribution_drift", "numeric_distribution_drift",
            name="detector_type"
        )
        drift_status.create(bind, checkfirst=True)
        drift_severity.create(bind, checkfirst=True)
        detector_type.create(bind, checkfirst=True)

    # 2. Create drift_runs Table
    op.create_table(
        "drift_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("baseline_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="no_drift"),
        sa.Column("overall_drift_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("drifted_columns_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_columns_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_drift_runs_dataset_id", "drift_runs", ["dataset_id"])
    op.create_index("ix_drift_runs_status", "drift_runs", ["status"])
    op.create_index("ix_drift_runs_created_at", "drift_runs", ["created_at"])

    # 3. Create drift_results Table
    op.create_table(
        "drift_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("drift_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("drift_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("column_name", sa.String(255), nullable=False),
        sa.Column("column_type", sa.String(64), nullable=False, server_default="numeric"),
        sa.Column("detector_type", sa.String(64), nullable=False),
        sa.Column("drift_detected", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("drift_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("threshold", sa.Float(), nullable=False, server_default="0.2"),
        sa.Column("severity", sa.String(32), nullable=False, server_default="info"),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("metrics_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_drift_results_drift_run_id", "drift_results", ["drift_run_id"])
    op.create_index("ix_drift_results_column_name", "drift_results", ["column_name"])
    op.create_index("ix_drift_results_detector_type", "drift_results", ["detector_type"])
    op.create_index("ix_drift_results_drift_detected", "drift_results", ["drift_detected"])


def downgrade() -> None:
    op.drop_table("drift_results")
    op.drop_table("drift_runs")
