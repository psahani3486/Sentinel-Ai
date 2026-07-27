"""
Sentinel AI — Incident Workspace Models

SQLAlchemy ORM models representing unified investigation incidents (Incident)
and chronological timeline events (IncidentEvent).
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
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import IncidentEventType, IncidentSeverity, IncidentStatus

if TYPE_CHECKING:
    from app.models.ai import RootCauseAnalysis
    from app.models.dataset import Dataset
    from app.models.forecasting import ForecastRun
    from app.models.recommendation import Recommendation


class Incident(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a unified investigation workspace incident correlating all platform signals.
    """

    __tablename__ = "incidents"

    __table_args__ = (
        Index("ix_incidents_dataset_id", "dataset_id"),
        Index("ix_incidents_status", "status"),
        Index("ix_incidents_severity", "severity"),
        Index("ix_incidents_created_at", "created_at"),
    )

    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    rca_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("root_cause_analyses.id", ondelete="SET NULL"),
        nullable=True,
    )
    recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recommendations.id", ondelete="SET NULL"),
        nullable=True,
    )
    forecast_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("forecast_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity", create_constraint=True),
        default=IncidentSeverity.HIGH,
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status", create_constraint=True),
        default=IncidentStatus.OPEN,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    root_cause_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    recommendations_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    forecast_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    related_datasets: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    related_jobs: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    related_alerts: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    resolved_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    rca: Mapped["RootCauseAnalysis | None"] = relationship("RootCauseAnalysis")
    recommendation: Mapped["Recommendation | None"] = relationship("Recommendation")
    forecast: Mapped["ForecastRun | None"] = relationship("ForecastRun")

    timeline_events: Mapped[list["IncidentEvent"]] = relationship(
        "IncidentEvent",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentEvent.timestamp.asc()",
    )

    def __repr__(self) -> str:
        return (
            f"<Incident(id={self.id}, title='{self.title}', status='{self.status.value}', "
            f"severity='{self.severity.value}')>"
        )


class IncidentEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an individual chronological event inside an Incident timeline.
    """

    __tablename__ = "incident_events"

    __table_args__ = (
        Index("ix_incident_events_incident_id", "incident_id"),
        Index("ix_incident_events_timestamp", "timestamp"),
        Index("ix_incident_events_created_at", "created_at"),
    )

    incident_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    event_type: Mapped[IncidentEventType] = mapped_column(
        Enum(IncidentEventType, name="incident_event_type", create_constraint=True),
        nullable=False,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="event_severity", create_constraint=True),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evidence_link: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    incident: Mapped["Incident"] = relationship("Incident", back_populates="timeline_events")

    def __repr__(self) -> str:
        return f"<IncidentEvent(id={self.id}, incident_id={self.incident_id}, type='{self.event_type.value}')>"
