"""
Sentinel AI — Data Drift Models

SQLAlchemy ORM models representing data drift execution runs (DriftRun)
and detailed per-column feature drift results (DriftResult).
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DetectorType, DriftSeverity, DriftStatus

if TYPE_CHECKING:
    from app.models.dataset import Dataset, DatasetVersion


class DriftRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an execution run of the Data Drift Detection Engine comparing
    a current dataset version against a baseline version.
    """

    __tablename__ = "drift_runs"

    __table_args__ = (
        Index("ix_drift_runs_dataset_id", "dataset_id"),
        Index("ix_drift_runs_status", "status"),
        Index("ix_drift_runs_created_at", "created_at"),
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    current_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    baseline_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[DriftStatus] = mapped_column(
        Enum(DriftStatus, name="drift_status", create_constraint=True),
        default=DriftStatus.NO_DRIFT,
        nullable=False,
    )
    overall_drift_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    drifted_columns_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_columns_analyzed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    summary: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset"] = relationship("Dataset")
    current_version: Mapped["DatasetVersion"] = relationship(
        "DatasetVersion", foreign_keys=[current_version_id]
    )
    baseline_version: Mapped["DatasetVersion"] = relationship(
        "DatasetVersion", foreign_keys=[baseline_version_id]
    )
    results: Mapped[list["DriftResult"]] = relationship(
        "DriftResult",
        back_populates="drift_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<DriftRun(id={self.id}, dataset_id={self.dataset_id}, "
            f"status={self.status.value}, score={self.overall_drift_score:.1f})>"
        )


class DriftResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Detailed evaluation result for a single column analyzed by a specific Drift Detector.
    """

    __tablename__ = "drift_results"

    __table_args__ = (
        Index("ix_drift_results_drift_run_id", "drift_run_id"),
        Index("ix_drift_results_column_name", "column_name"),
        Index("ix_drift_results_detector_type", "detector_type"),
        Index("ix_drift_results_drift_detected", "drift_detected"),
    )

    drift_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("drift_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    column_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    column_type: Mapped[str] = mapped_column(
        String(64),
        default="numeric",
        nullable=False,
    )
    detector_type: Mapped[DetectorType] = mapped_column(
        Enum(DetectorType, name="detector_type", create_constraint=True),
        nullable=False,
    )
    drift_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    drift_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    threshold: Mapped[float] = mapped_column(
        Float,
        default=0.2,
        nullable=False,
    )
    severity: Mapped[DriftSeverity] = mapped_column(
        Enum(DriftSeverity, name="drift_severity", create_constraint=True),
        default=DriftSeverity.INFO,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metrics_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    drift_run: Mapped["DriftRun"] = relationship("DriftRun", back_populates="results")

    def __repr__(self) -> str:
        return (
            f"<DriftResult(id={self.id}, col='{self.column_name}', detector={self.detector_type.value}, "
            f"detected={self.drift_detected}, score={self.drift_score:.4f})>"
        )
