"""
Sentinel AI — Recommendation Models

SQLAlchemy ORM models representing AI remediation recommendations (Recommendation)
and granular supporting evidence telemetry items (RecommendationEvidence).
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
from app.models.enums import RecommendationCategory, RecommendationPriority

if TYPE_CHECKING:
    from app.models.ai import RootCauseAnalysis
    from app.models.dataset import Dataset


class Recommendation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a prioritized, actionable remediation recommendation entity.
    """

    __tablename__ = "recommendations"

    __table_args__ = (
        Index("ix_recommendations_rca_id", "rca_id"),
        Index("ix_recommendations_dataset_id", "dataset_id"),
        Index("ix_recommendations_category", "category"),
        Index("ix_recommendations_priority", "priority"),
        Index("ix_recommendations_priority_score", "priority_score"),
        Index("ix_recommendations_created_at", "created_at"),
    )

    rca_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("root_cause_analyses.id", ondelete="SET NULL"),
        nullable=True,
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    category: Mapped[RecommendationCategory] = mapped_column(
        Enum(RecommendationCategory, name="recommendation_category", create_constraint=True),
        nullable=False,
    )
    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(RecommendationPriority, name="recommendation_priority", create_constraint=True),
        default=RecommendationPriority.MEDIUM,
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
    estimated_impact: Mapped[str] = mapped_column(
        String(32),
        default="HIGH",
        nullable=False,
    )
    estimated_effort: Mapped[str] = mapped_column(
        String(32),
        default="LOW",
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    priority_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    suggested_next_steps: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    rca: Mapped["RootCauseAnalysis | None"] = relationship("RootCauseAnalysis")
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    evidences: Mapped[list["RecommendationEvidence"]] = relationship(
        "RecommendationEvidence",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation(id={self.id}, category='{self.category.value}', "
            f"priority='{self.priority.value}', score={self.priority_score:.1f})>"
        )


class RecommendationEvidence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents supporting telemetry, log, or RCA evidence attached to a Recommendation entity.
    """

    __tablename__ = "recommendation_evidences"

    __table_args__ = (
        Index("ix_recommendation_evidences_recommendation_id", "recommendation_id"),
        Index("ix_recommendation_evidences_created_at", "created_at"),
    )

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"),
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
    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="evidences")

    def __repr__(self) -> str:
        return f"<RecommendationEvidence(id={self.id}, recommendation_id={self.recommendation_id}, title='{self.title}')>"
