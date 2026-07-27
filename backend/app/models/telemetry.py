"""
Sentinel AI — Platform Telemetry & APM Tracing Models

SQLAlchemy ORM models representing internal metric snapshots (MetricSnapshot),
APM distributed trace contexts (Trace), and execution waterfall spans (Span).
"""

import datetime
import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import MetricType, SpanStatus


class MetricSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an internal platform metric snapshot.
    """

    __tablename__ = "metric_snapshots"

    __table_args__ = (
        Index("ix_metric_snapshots_metric_name", "metric_name"),
        Index("ix_metric_snapshots_metric_type", "metric_type"),
        Index("ix_metric_snapshots_created_at", "created_at"),
    )

    metric_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType, name="metric_type", create_constraint=True),
        default=MetricType.LATENCY,
        nullable=False,
    )
    value: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    unit: Mapped[str] = mapped_column(
        String(32),
        default="ms",
        nullable=False,
    )
    labels: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<MetricSnapshot(id={self.id}, name='{self.metric_name}', value={self.value}{self.unit})>"


class Trace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an APM distributed trace context.
    """

    __tablename__ = "traces"

    __table_args__ = (
        Index("ix_traces_trace_id", "trace_id", unique=True),
        Index("ix_traces_service_name", "service_name"),
        Index("ix_traces_status", "status"),
        Index("ix_traces_created_at", "created_at"),
    )

    trace_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    service_name: Mapped[str] = mapped_column(
        String(128),
        default="sentinel-api",
        nullable=False,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    status: Mapped[SpanStatus] = mapped_column(
        Enum(SpanStatus, name="span_status", create_constraint=True),
        default=SpanStatus.OK,
        nullable=False,
    )
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    spans: Mapped[list["Span"]] = relationship(
        "Span",
        back_populates="trace",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Trace(id={self.id}, trace_id='{self.trace_id}', duration={self.duration_ms}ms)>"


class Span(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an individual execution waterfall span inside a Trace context.
    """

    __tablename__ = "spans"

    __table_args__ = (
        Index("ix_spans_span_id", "span_id", unique=True),
        Index("ix_spans_trace_id_str", "trace_id_str"),
        Index("ix_spans_parent_span_id", "parent_span_id"),
        Index("ix_spans_created_at", "created_at"),
    )

    trace_pk: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("traces.id", ondelete="CASCADE"),
        nullable=False,
    )
    span_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    trace_id_str: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    parent_span_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    service_name: Mapped[str] = mapped_column(
        String(128),
        default="sentinel-api",
        nullable=False,
    )
    status: Mapped[SpanStatus] = mapped_column(
        Enum(SpanStatus, name="span_status", create_constraint=True),
        default=SpanStatus.OK,
        nullable=False,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    attributes: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    trace: Mapped["Trace"] = relationship("Trace", back_populates="spans")

    def __repr__(self) -> str:
        return f"<Span(id={self.id}, span_id='{self.span_id}', name='{self.name}')>"
