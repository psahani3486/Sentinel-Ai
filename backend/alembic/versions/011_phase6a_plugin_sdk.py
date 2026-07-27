"""Phase 6A — Enterprise Plugin & Extension SDK Schema

Revision ID: 011_phase6a_plugin_sdk
Revises: 010_phase5b_workflow_engine
Create Date: 2026-07-27 08:48:00.000000

Creates:
- Enum types: plugin_status, plugin_type
- Tables: plugins, plugin_installations
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_phase6a_plugin_sdk"
down_revision: str | None = "010_phase5b_workflow_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        plugin_status = postgresql.ENUM(
            "discovered", "validated", "loaded", "enabled",
            "disabled", "error", "unloaded", name="plugin_status"
        )
        plugin_type = postgresql.ENUM(
            "connector", "validation_rule", "profiling", "drift_detector",
            "alert_rule", "analyzer", "recommendation", "forecast",
            "workflow", "dashboard_widget", name="plugin_type"
        )
        plugin_status.create(bind, checkfirst=True)
        plugin_type.create(bind, checkfirst=True)

    # 2. Create plugins Table
    op.create_table(
        "plugins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plugin_id", sa.String(128), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("plugin_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="discovered"),
        sa.Column("entry_point", sa.String(255), nullable=False),
        sa.Column("minimum_platform_version", sa.String(64), nullable=False, server_default="1.0.0"),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column("manifest_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_plugins_plugin_id", "plugins", ["plugin_id"], unique=True)
    op.create_index("ix_plugins_plugin_type", "plugins", ["plugin_type"])
    op.create_index("ix_plugins_status", "plugins", ["status"])
    op.create_index("ix_plugins_created_at", "plugins", ["created_at"])

    # 3. Create plugin_installations Table
    op.create_table(
        "plugin_installations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("installed_by", sa.String(255), nullable=False, server_default="system"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("configuration", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_plugin_installations_plugin_id", "plugin_installations", ["plugin_id"])
    op.create_index("ix_plugin_installations_created_at", "plugin_installations", ["created_at"])


def downgrade() -> None:
    op.drop_table("plugin_installations")
    op.drop_table("plugins")
