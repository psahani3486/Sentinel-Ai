"""Phase 6B — Enterprise Data Catalog, Lineage & Governance Schema

Revision ID: 012_phase6b_catalog_engine
Revises: 011_phase6a_plugin_sdk
Create Date: 2026-07-27 08:57:00.000000

Creates:
- Enum types: asset_type, data_sensitivity, lifecycle_status
- Tables: catalog_assets, catalog_lineages, glossary_terms, governance_policies
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_phase6b_catalog_engine"
down_revision: str | None = "011_phase6a_plugin_sdk"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Enums if PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        asset_type = postgresql.ENUM(
            "dataset", "table", "column", "pipeline", "model", "dashboard", name="asset_type"
        )
        data_sensitivity = postgresql.ENUM(
            "public", "internal", "confidential", "restricted", "pii", name="data_sensitivity"
        )
        lifecycle_status = postgresql.ENUM(
            "proposed", "active", "deprecated", "archived", name="lifecycle_status"
        )
        asset_type.create(bind, checkfirst=True)
        data_sensitivity.create(bind, checkfirst=True)
        lifecycle_status.create(bind, checkfirst=True)

    # 2. Create catalog_assets Table
    op.create_table(
        "catalog_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("asset_type", sa.String(32), nullable=False, server_default="dataset"),
        sa.Column("domain", sa.String(128), nullable=False, server_default="General"),
        sa.Column("owner", sa.String(255), nullable=False, server_default="Data Engineering"),
        sa.Column("steward", sa.String(255), nullable=False, server_default="Governance Lead"),
        sa.Column("business_description", sa.Text(), nullable=False),
        sa.Column("technical_description", sa.Text(), nullable=False),
        sa.Column("sensitivity", sa.String(32), nullable=False, server_default="internal"),
        sa.Column("retention_period_days", sa.Integer(), nullable=False, server_default="365"),
        sa.Column("lifecycle_status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("classifications", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_catalog_assets_name", "catalog_assets", ["name"])
    op.create_index("ix_catalog_assets_asset_type", "catalog_assets", ["asset_type"])
    op.create_index("ix_catalog_assets_domain", "catalog_assets", ["domain"])
    op.create_index("ix_catalog_assets_sensitivity", "catalog_assets", ["sensitivity"])
    op.create_index("ix_catalog_assets_dataset_id", "catalog_assets", ["dataset_id"])
    op.create_index("ix_catalog_assets_created_at", "catalog_assets", ["created_at"])

    # 3. Create catalog_lineages Table
    op.create_table(
        "catalog_lineages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("catalog_assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("catalog_assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship_type", sa.String(64), nullable=False, server_default="TRANSFORMS"),
        sa.Column("lineage_dag", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_catalog_lineages_source_asset_id", "catalog_lineages", ["source_asset_id"])
    op.create_index("ix_catalog_lineages_target_asset_id", "catalog_lineages", ["target_asset_id"])
    op.create_index("ix_catalog_lineages_created_at", "catalog_lineages", ["created_at"])

    # 4. Create glossary_terms Table
    op.create_table(
        "glossary_terms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("term", sa.String(128), nullable=False, unique=True),
        sa.Column("definition", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(128), nullable=False, server_default="General"),
        sa.Column("related_assets", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_glossary_terms_term", "glossary_terms", ["term"], unique=True)
    op.create_index("ix_glossary_terms_domain", "glossary_terms", ["domain"])
    op.create_index("ix_glossary_terms_created_at", "glossary_terms", ["created_at"])

    # 5. Create governance_policies Table
    op.create_table(
        "governance_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("policy_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(128), nullable=False, server_default="Data Quality"),
        sa.Column("rules_definition", sa.JSON(), nullable=True),
        sa.Column("compliance_status", sa.String(64), nullable=False, server_default="COMPLIANT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_governance_policies_policy_name", "governance_policies", ["policy_name"])
    op.create_index("ix_governance_policies_category", "governance_policies", ["category"])
    op.create_index("ix_governance_policies_created_at", "governance_policies", ["created_at"])


def downgrade() -> None:
    op.drop_table("governance_policies")
    op.drop_table("glossary_terms")
    op.drop_table("catalog_lineages")
    op.drop_table("catalog_assets")
