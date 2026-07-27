"""
Sentinel AI — Dataset Models

Defines ORM entities for datasets, dataset versions, schema definitions,
column metadata, and statistical data profiles.
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ConnectorType, DatasetType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.validation import ValidationRun


class Dataset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Data asset registered in Sentinel AI.

    Tracks ownership, connector configuration, dataset type, and soft-deletion status.
    """

    __tablename__ = "datasets"

    __table_args__ = (
        Index("ix_datasets_name", "name"),
        Index("ix_datasets_owner_id", "owner_id"),
        Index("ix_datasets_dataset_type", "dataset_type"),
        Index("ix_datasets_connector_type", "connector_type"),
        Index("ix_datasets_is_active", "is_active"),
        Index("ix_datasets_created_at", "created_at"),
        UniqueConstraint("owner_id", "name", name="uq_datasets_owner_name"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    dataset_type: Mapped[DatasetType] = mapped_column(
        Enum(DatasetType, name="dataset_type", create_constraint=True),
        default=DatasetType.TABULAR,
        nullable=False,
    )
    connector_type: Mapped[ConnectorType] = mapped_column(
        Enum(ConnectorType, name="connector_type", create_constraint=True),
        default=ConnectorType.CSV,
        nullable=False,
    )
    connection_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    owner: Mapped["User"] = relationship("User", backref="datasets")
    versions: Mapped[list["DatasetVersion"]] = relationship(
        "DatasetVersion",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="DatasetVersion.version_number.desc()",
    )
    validation_runs: Mapped[list["ValidationRun"]] = relationship(
        "ValidationRun",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name='{self.name}', type={self.dataset_type.value})>"


class DatasetVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Immutable version snapshot of a dataset.

    Tracks storage location, file metrics, checksum, and ingestion lineage.
    """

    __tablename__ = "dataset_versions"

    __table_args__ = (
        Index("ix_dataset_versions_dataset_id", "dataset_id"),
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_versions_dataset_version"),
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    storage_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    row_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    column_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    checksum: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    ingested_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped[Dataset] = relationship("Dataset", back_populates="versions")
    ingested_by: Mapped["User | None"] = relationship("User")
    schema_info: Mapped["DatasetSchema | None"] = relationship(
        "DatasetSchema",
        back_populates="version",
        uselist=False,
        cascade="all, delete-orphan",
    )
    profile: Mapped["DatasetProfile | None"] = relationship(
        "DatasetProfile",
        back_populates="version",
        uselist=False,
        cascade="all, delete-orphan",
    )
    validation_runs: Mapped[list["ValidationRun"]] = relationship(
        "ValidationRun",
        back_populates="version",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<DatasetVersion(id={self.id}, dataset_id={self.dataset_id}, v={self.version_number})>"


class DatasetSchema(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Schema header definition for a specific DatasetVersion.
    """

    __tablename__ = "dataset_schemas"

    __table_args__ = (
        Index("ix_dataset_schemas_version_id", "dataset_version_id"),
    )

    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    column_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    version: Mapped[DatasetVersion] = relationship("DatasetVersion", back_populates="schema_info")
    columns: Mapped[list["DatasetColumn"]] = relationship(
        "DatasetColumn",
        back_populates="schema_info",
        cascade="all, delete-orphan",
        order_by="DatasetColumn.position",
    )

    def __repr__(self) -> str:
        return f"<DatasetSchema(id={self.id}, version_id={self.dataset_version_id}, cols={self.column_count})>"


class DatasetColumn(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Individual column metadata belonging to a DatasetSchema.
    """

    __tablename__ = "dataset_columns"

    __table_args__ = (
        Index("ix_dataset_columns_schema_id", "dataset_schema_id"),
        Index("ix_dataset_columns_name", "column_name"),
        UniqueConstraint("dataset_schema_id", "column_name", name="uq_dataset_columns_schema_name"),
    )

    dataset_schema_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_schemas.id", ondelete="CASCADE"),
        nullable=False,
    )
    column_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    data_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    is_nullable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_primary_key: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    sample_values: Mapped[list[Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    schema_info: Mapped[DatasetSchema] = relationship("DatasetSchema", back_populates="columns")

    def __repr__(self) -> str:
        return f"<DatasetColumn(id={self.id}, name='{self.column_name}', type='{self.data_type}')>"


class DatasetProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Automated statistical data profile for a DatasetVersion.

    Stores row count, column count, memory size, and comprehensive per-column statistics in profile_data JSON.
    """

    __tablename__ = "dataset_profiles"

    __table_args__ = (
        Index("ix_dataset_profiles_version_id", "dataset_version_id"),
    )

    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    total_rows: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    total_columns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    memory_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    profile_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    version: Mapped[DatasetVersion] = relationship("DatasetVersion", back_populates="profile")

    def __repr__(self) -> str:
        return f"<DatasetProfile(id={self.id}, version_id={self.dataset_version_id}, rows={self.total_rows})>"
