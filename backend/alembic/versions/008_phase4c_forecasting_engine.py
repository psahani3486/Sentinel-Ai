"""Phase 4C — Predictive Observability & Risk Forecasting Schema

Revision ID: 008_phase4c_forecasting_engine
Revises: 007_phase4b_recommendation_engine
Create Date: 2026-07-26 19:48:00.000000

Creates:
- Enum types: forecast_type, trend_direction, risk_level
- Tables: forecast_runs, forecast_results
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008_phase4c_forecasting_engine"
down_revision: str | None = "007_phase4b_recommendation_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        forecast_type = postgresql.ENUM(
            "quality_score_trend", "data_drift_trend", "validation_failure_probability",
            "pipeline_failure_probability", "job_failure_probability", "dataset_freshness_forecast",
            "alert_volume_forecast", "connector_reliability_forecast", name="forecast_type"
        )
        trend_direction = postgresql.ENUM("upward", "downward", "stable", name="trend_direction")
        risk_level = postgresql.ENUM("critical", "high", "medium", "low", "info", name="risk_level")
        forecast_type.create(bind, checkfirst=True)
        trend_direction.create(bind, checkfirst=True)
        risk_level.create(bind, checkfirst=True)

    # 2. Create forecast_runs Table
    op.create_table(
        "forecast_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("forecast_type", sa.String(64), nullable=False),
        sa.Column("algorithm_name", sa.String(64), nullable=False, server_default="LinearRegression"),
        sa.Column("forecast_horizon_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("overall_risk_level", sa.String(32), nullable=False, server_default="low"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_forecast_runs_dataset_id", "forecast_runs", ["dataset_id"])
    op.create_index("ix_forecast_runs_forecast_type", "forecast_runs", ["forecast_type"])
    op.create_index("ix_forecast_runs_overall_risk_level", "forecast_runs", ["overall_risk_level"])
    op.create_index("ix_forecast_runs_created_at", "forecast_runs", ["created_at"])

    # 3. Create forecast_results Table
    op.create_table(
        "forecast_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("forecast_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("forecast_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_metric", sa.String(128), nullable=False),
        sa.Column("predicted_value", sa.Float(), nullable=False),
        sa.Column("confidence_interval_lower", sa.Float(), nullable=False),
        sa.Column("confidence_interval_upper", sa.Float(), nullable=False),
        sa.Column("trend_direction", sa.String(32), nullable=False, server_default="stable"),
        sa.Column("risk_level", sa.String(32), nullable=False, server_default="low"),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("preventive_actions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_forecast_results_forecast_run_id", "forecast_results", ["forecast_run_id"])
    op.create_index("ix_forecast_results_created_at", "forecast_results", ["created_at"])


def downgrade() -> None:
    op.drop_table("forecast_results")
    op.drop_table("forecast_runs")
