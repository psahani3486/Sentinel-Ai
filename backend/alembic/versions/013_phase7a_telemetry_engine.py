"""Phase 7A — Platform Telemetry, Metrics & Distributed Tracing Schema

Revision ID: 013_phase7a_telemetry_engine
Revises: 012_phase6b_catalog_engine
Create Date: 2026-07-27 09:06:00.000000

Creates:
- Enum types: metric_type, span_status, health_status
- Tables: metric_snapshots, traces, spans
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013_phase7a_telemetry_engine"
down_revision: str | None = "012_phase6b_catalog_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        metric_type = postgresql.ENUM(
            "latency", "throughput", "request_count", "error_count",
            "worker_utilization", "queue_depth", "duration", name="metric_type"
        )
        span_status = postgresql.ENUM("ok", "error", "unset", name="span_status")
        health_status = postgresql.ENUM("healthy", "degraded", "unhealthy", name="health_status")
        metric_type.create(bind, checkfirst=True)
        span_status.create(bind, checkfirst=True)
        health_status.create(bind, checkfirst=True)

    # 2. Create metric_snapshots Table
    op.create_table(
        "metric_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("metric_name", sa.String(128), nullable=False),
        sa.Column("metric_type", sa.String(32), nullable=False, server_default="latency"),
        sa.Column("value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit", sa.String(32), nullable=False, server_default="ms"),
        sa.Column("labels", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_metric_snapshots_metric_name", "metric_snapshots", ["metric_name"])
    op.create_index("ix_metric_snapshots_metric_type", "metric_snapshots", ["metric_type"])
    op.create_index("ix_metric_snapshots_created_at", "metric_snapshots", ["created_at"])

    # 3. Create traces Table
    op.create_table(
        "traces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trace_id", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("service_name", sa.String(128), nullable=False, server_default="sentinel-api"),
        sa.Column("duration_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="ok"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_traces_trace_id", "traces", ["trace_id"], unique=True)
    op.create_index("ix_traces_service_name", "traces", ["service_name"])
    op.create_index("ix_traces_status", "traces", ["status"])
    op.create_index("ix_traces_created_at", "traces", ["created_at"])

    # 4. Create spans Table
    op.create_table(
        "spans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trace_pk", postgresql.UUID(as_uuid=True), sa.ForeignKey("traces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("span_id", sa.String(64), nullable=False, unique=True),
        sa.Column("trace_id_str", sa.String(64), nullable=False),
        sa.Column("parent_span_id", sa.String(64), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("service_name", sa.String(128), nullable=False, server_default="sentinel-api"),
        sa.Column("status", sa.String(32), nullable=False, server_default="ok"),
        sa.Column("duration_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_spans_span_id", "spans", ["span_id"], unique=True)
    op.create_index("ix_spans_trace_id_str", "spans", ["trace_id_str"])
    op.create_index("ix_spans_parent_span_id", "spans", ["parent_span_id"])
    op.create_index("ix_spans_created_at", "spans", ["created_at"])


def downgrade() -> None:
    op.drop_table("spans")
    op.drop_table("traces")
    op.drop_table("metric_snapshots")
