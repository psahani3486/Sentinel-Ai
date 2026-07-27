"""
Sentinel AI — Alert Models

SQLAlchemy ORM models representing incident alerts (Alert) and deduplicated
historical occurrence events (AlertOccurrence).
"""

import datetime
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AlertSeverity, AlertStatus, AlertType

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.user import User


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an active or historical incident alert entity.
    Supports deduplication via fingerprint hash, occurrence counting, and escalation logic.
    """

    __tablename__ = "alerts"

    __table_args__ = (
        Index("ix_alerts_fingerprint", "fingerprint"),
        Index("ix_alerts_dataset_id", "dataset_id"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_alert_type", "alert_type"),
        Index("ix_alerts_created_at", "created_at"),
    )

    fingerprint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    alert_type: Mapped[AlertType] = mapped_column(
        Enum(AlertType, name="alert_type", create_constraint=True),
        nullable=False,
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status", create_constraint=True),
        default=AlertStatus.OPEN,
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity", create_constraint=True),
        default=AlertSeverity.INFO,
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
    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    first_seen_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
    last_seen_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
    acknowledged_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    acknowledged_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    alert_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    acknowledged_by: Mapped["User | None"] = relationship("User", foreign_keys=[acknowledged_by_id])
    resolved_by: Mapped["User | None"] = relationship("User", foreign_keys=[resolved_by_id])
    occurrences: Mapped[list["AlertOccurrence"]] = relationship(
        "AlertOccurrence",
        back_populates="alert",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.id}, type='{self.alert_type.value}', status='{self.status.value}', "
            f"severity='{self.severity.value}', count={self.occurrence_count})>"
        )


class AlertOccurrence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Tracks each deduplicated occurrence event associated with a parent Alert instance.
    """

    __tablename__ = "alert_occurrences"

    __table_args__ = (
        Index("ix_alert_occurrences_alert_id", "alert_id"),
        Index("ix_alert_occurrences_created_at", "created_at"),
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity_occurrence", create_constraint=True),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    event_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    alert: Mapped["Alert"] = relationship("Alert", back_populates="occurrences")

    def __repr__(self) -> str:
        return f"<AlertOccurrence(id={self.id}, alert_id={self.alert_id}, severity='{self.severity.value}')>"
