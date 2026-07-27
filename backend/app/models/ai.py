"""
Sentinel AI — AI Root Cause Analysis Models

SQLAlchemy ORM models representing structured AI Root Cause Analysis reports (RootCauseAnalysis)
and granular diagnostic evidence items (AnalysisEvidence).
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AnalysisStatus, AnalysisType, ValidationSeverity

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class RootCauseAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an AI Root Cause Analysis report entity for an incident, failure, or drift event.
    """

    __tablename__ = "root_cause_analyses"

    __table_args__ = (
        Index("ix_root_cause_analyses_target_entity_id", "target_entity_id"),
        Index("ix_root_cause_analyses_dataset_id", "dataset_id"),
        Index("ix_root_cause_analyses_analysis_type", "analysis_type"),
        Index("ix_root_cause_analyses_created_at", "created_at"),
    )

    analysis_type: Mapped[AnalysisType] = mapped_column(
        Enum(AnalysisType, name="analysis_type", create_constraint=True),
        nullable=False,
    )
    target_entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    target_entity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    probable_root_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    severity: Mapped[ValidationSeverity] = mapped_column(
        Enum(ValidationSeverity, name="analysis_severity", create_constraint=True),
        default=ValidationSeverity.INFO,
        nullable=False,
    )
    affected_components: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    recommended_actions: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, name="analysis_status", create_constraint=True),
        default=AnalysisStatus.COMPLETED,
        nullable=False,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    llm_provider_name: Mapped[str] = mapped_column(
        String(64),
        default="MockLLMProvider",
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    evidences: Mapped[list["AnalysisEvidence"]] = relationship(
        "AnalysisEvidence",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<RootCauseAnalysis(id={self.id}, type='{self.analysis_type.value}', "
            f"target='{self.target_entity_id}', confidence={self.confidence_score:.1f}%)>"
        )


class AnalysisEvidence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents supporting metric, log, rule, or statistical evidence attached to an RCA report.
    """

    __tablename__ = "analysis_evidences"

    __table_args__ = (
        Index("ix_analysis_evidences_analysis_id", "analysis_id"),
        Index("ix_analysis_evidences_created_at", "created_at"),
    )

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("root_cause_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evidence_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    analysis: Mapped["RootCauseAnalysis"] = relationship("RootCauseAnalysis", back_populates="evidences")

    def __repr__(self) -> str:
        return f"<AnalysisEvidence(id={self.id}, analysis_id={self.analysis_id}, title='{self.title}')>"
