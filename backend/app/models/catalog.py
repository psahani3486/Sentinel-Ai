"""
Sentinel AI — Data Catalog, Lineage & Governance Models

SQLAlchemy ORM models representing cataloged data assets (CatalogAsset),
cross-layer lineage DAG edges (CatalogLineage), business glossary terms (GlossaryTerm),
and governance compliance policies (GovernancePolicy).
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AssetType, DataSensitivity, LifecycleStatus

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class CatalogAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a cataloged metadata asset in Sentinel AI.
    """

    __tablename__ = "catalog_assets"

    __table_args__ = (
        Index("ix_catalog_assets_name", "name"),
        Index("ix_catalog_assets_asset_type", "asset_type"),
        Index("ix_catalog_assets_domain", "domain"),
        Index("ix_catalog_assets_sensitivity", "sensitivity"),
        Index("ix_catalog_assets_dataset_id", "dataset_id"),
        Index("ix_catalog_assets_created_at", "created_at"),
    )

    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type", create_constraint=True),
        default=AssetType.DATASET,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String(128),
        default="General",
        nullable=False,
    )
    owner: Mapped[str] = mapped_column(
        String(255),
        default="Data Engineering",
        nullable=False,
    )
    steward: Mapped[str] = mapped_column(
        String(255),
        default="Governance Lead",
        nullable=False,
    )
    business_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    technical_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    sensitivity: Mapped[DataSensitivity] = mapped_column(
        Enum(DataSensitivity, name="data_sensitivity", create_constraint=True),
        default=DataSensitivity.INTERNAL,
        nullable=False,
    )
    retention_period_days: Mapped[int] = mapped_column(
        Integer,
        default=365,
        nullable=False,
    )
    lifecycle_status: Mapped[LifecycleStatus] = mapped_column(
        Enum(LifecycleStatus, name="lifecycle_status", create_constraint=True),
        default=LifecycleStatus.ACTIVE,
        nullable=False,
    )
    tags: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    classifications: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    outgoing_lineages: Mapped[list["CatalogLineage"]] = relationship(
        "CatalogLineage",
        foreign_keys="CatalogLineage.source_asset_id",
        back_populates="source_asset",
        cascade="all, delete-orphan",
    )
    incoming_lineages: Mapped[list["CatalogLineage"]] = relationship(
        "CatalogLineage",
        foreign_keys="CatalogLineage.target_asset_id",
        back_populates="target_asset",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CatalogAsset(id={self.id}, name='{self.name}', type='{self.asset_type.value}')>"


class CatalogLineage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a directed lineage DAG edge connecting source and target catalog assets.
    """

    __tablename__ = "catalog_lineages"

    __table_args__ = (
        Index("ix_catalog_lineages_source_asset_id", "source_asset_id"),
        Index("ix_catalog_lineages_target_asset_id", "target_asset_id"),
        Index("ix_catalog_lineages_created_at", "created_at"),
    )

    source_asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("catalog_assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("catalog_assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(64),
        default="TRANSFORMS",
        nullable=False,
    )
    lineage_dag: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    source_asset: Mapped["CatalogAsset"] = relationship(
        "CatalogAsset", foreign_keys=[source_asset_id], back_populates="outgoing_lineages"
    )
    target_asset: Mapped["CatalogAsset"] = relationship(
        "CatalogAsset", foreign_keys=[target_asset_id], back_populates="incoming_lineages"
    )

    def __repr__(self) -> str:
        return f"<CatalogLineage(id={self.id}, source={self.source_asset_id}, target={self.target_asset_id})>"


class GlossaryTerm(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a Business Glossary Term.
    """

    __tablename__ = "glossary_terms"

    __table_args__ = (
        Index("ix_glossary_terms_term", "term", unique=True),
        Index("ix_glossary_terms_domain", "domain"),
        Index("ix_glossary_terms_created_at", "created_at"),
    )

    term: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )
    definition: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String(128),
        default="General",
        nullable=False,
    )
    related_assets: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<GlossaryTerm(id={self.id}, term='{self.term}')>"


class GovernancePolicy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a Data Governance Policy.
    """

    __tablename__ = "governance_policies"

    __table_args__ = (
        Index("ix_governance_policies_policy_name", "policy_name"),
        Index("ix_governance_policies_category", "category"),
        Index("ix_governance_policies_created_at", "created_at"),
    )

    policy_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(128),
        default="Data Quality",
        nullable=False,
    )
    rules_definition: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    compliance_status: Mapped[str] = mapped_column(
        String(64),
        default="COMPLIANT",
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<GovernancePolicy(id={self.id}, name='{self.policy_name}', status='{self.compliance_status}')>"
