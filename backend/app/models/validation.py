"""
Sentinel AI — Validation Models

Defines ORM entities for validation rules, validation run executions,
and detailed rule execution results.
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RuleType, RunStatus, ValidationSeverity, ValidationStatus

if TYPE_CHECKING:
    from app.models.dataset import Dataset, DatasetVersion
    from app.models.user import User


class ValidationRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Data quality rule definition.

    Defines rule parameters, target fields, severity, and rule type logic.
    """

    __tablename__ = "validation_rules"

    __table_args__ = (
        Index("ix_validation_rules_rule_type", "rule_type"),
        Index("ix_validation_rules_severity", "severity"),
        Index("ix_validation_rules_is_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    rule_type: Mapped[RuleType] = mapped_column(
        Enum(RuleType, name="rule_type", create_constraint=True),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    severity: Mapped[ValidationSeverity] = mapped_column(
        Enum(ValidationSeverity, name="validation_severity", create_constraint=True),
        default=ValidationSeverity.MEDIUM,
        nullable=False,
    )
    parameters: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    results: Mapped[list["ValidationResult"]] = relationship(
        "ValidationResult",
        back_populates="rule",
    )

    def __repr__(self) -> str:
        return f"<ValidationRule(id={self.id}, name='{self.name}', type={self.rule_type.value})>"


class ValidationRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Execution of a validation suite against a DatasetVersion.

    Captures status, execution duration, overall score, and category score breakdowns.
    """

    __tablename__ = "validation_runs"

    __table_args__ = (
        Index("ix_validation_runs_dataset_id", "dataset_id"),
        Index("ix_validation_runs_dataset_version_id", "dataset_version_id"),
        Index("ix_validation_runs_status", "status"),
        Index("ix_validation_runs_created_at", "created_at"),
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="run_status", create_constraint=True),
        default=RunStatus.PENDING,
        nullable=False,
    )
    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    completeness_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    consistency_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    accuracy_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    freshness_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    triggered_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="validation_runs")
    version: Mapped["DatasetVersion"] = relationship("DatasetVersion", back_populates="validation_runs")
    triggered_by: Mapped["User | None"] = relationship("User")
    results: Mapped[list["ValidationResult"]] = relationship(
        "ValidationResult",
        back_populates="run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ValidationRun(id={self.id}, version_id={self.dataset_version_id}, status={self.status.value}, score={self.overall_score})>"


class ValidationResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Outcome of an individual ValidationRule evaluated during a ValidationRun.

    Details rule status, message, affected columns, affected rows count, score impact, and sample diagnostics.
    """

    __tablename__ = "validation_results"

    __table_args__ = (
        Index("ix_validation_results_run_id", "validation_run_id"),
        Index("ix_validation_results_rule_id", "rule_id"),
        Index("ix_validation_results_status", "status"),
        Index("ix_validation_results_severity", "severity"),
    )

    validation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("validation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("validation_rules.id", ondelete="SET NULL"),
        nullable=True,
    )
    rule_type: Mapped[RuleType] = mapped_column(
        Enum(RuleType, name="rule_type", create_constraint=True),
        nullable=False,
    )
    status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus, name="validation_status", create_constraint=True),
        nullable=False,
    )
    severity: Mapped[ValidationSeverity] = mapped_column(
        Enum(ValidationSeverity, name="validation_severity", create_constraint=True),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    affected_columns: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    affected_rows_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    score_impact: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    run: Mapped[ValidationRun] = relationship("ValidationRun", back_populates="results")
    rule: Mapped[ValidationRule | None] = relationship("ValidationRule", back_populates="results")

    def __repr__(self) -> str:
        return f"<ValidationResult(id={self.id}, run_id={self.validation_run_id}, status={self.status.value})>"
