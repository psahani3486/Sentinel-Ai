"""
Sentinel AI — Enterprise Policy Engine & Governance Models

SQLAlchemy ORM models representing policy rule definitions (PolicyDefinition)
and historical evaluation compliance results (PolicyEvaluation).
"""

import datetime
import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PolicyCategory, PolicySeverity, PolicyStatus


class PolicyDefinition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an enterprise policy rule definition.
    """

    __tablename__ = "policy_definitions"

    __table_args__ = (
        Index("ix_policy_definitions_policy_name", "policy_name", unique=True),
        Index("ix_policy_definitions_category", "category"),
        Index("ix_policy_definitions_severity", "severity"),
        Index("ix_policy_definitions_is_active", "is_active"),
        Index("ix_policy_definitions_created_at", "created_at"),
    )

    policy_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    category: Mapped[PolicyCategory] = mapped_column(
        Enum(PolicyCategory, name="policy_category", create_constraint=True),
        default=PolicyCategory.DATASET_GOVERNANCE,
        nullable=False,
    )
    severity: Mapped[PolicySeverity] = mapped_column(
        Enum(PolicySeverity, name="policy_severity", create_constraint=True),
        default=PolicySeverity.HIGH,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    rules_spec: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    evaluations: Mapped[list["PolicyEvaluation"]] = relationship(
        "PolicyEvaluation",
        back_populates="policy_definition",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PolicyDefinition(id={self.id}, name='{self.policy_name}', category='{self.category.value}')>"


class PolicyEvaluation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an individual policy evaluation result.
    """

    __tablename__ = "policy_evaluations"

    __table_args__ = (
        Index("ix_policy_evaluations_policy_id", "policy_id"),
        Index("ix_policy_evaluations_status", "status"),
        Index("ix_policy_evaluations_severity", "severity"),
        Index("ix_policy_evaluations_evaluated_at", "evaluated_at"),
        Index("ix_policy_evaluations_created_at", "created_at"),
    )

    policy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("policy_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, name="policy_status", create_constraint=True),
        default=PolicyStatus.PASS,
        nullable=False,
    )
    severity: Mapped[PolicySeverity] = mapped_column(
        Enum(PolicySeverity, name="policy_severity", create_constraint=True),
        default=PolicySeverity.HIGH,
        nullable=False,
    )
    evidence: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evaluated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    policy_definition: Mapped["PolicyDefinition"] = relationship(
        "PolicyDefinition", back_populates="evaluations"
    )

    def __repr__(self) -> str:
        return f"<PolicyEvaluation(id={self.id}, status='{self.status.value}', severity='{self.severity.value}')>"
