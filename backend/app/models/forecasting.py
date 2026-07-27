"""
Sentinel AI — Forecasting Models

SQLAlchemy ORM models representing predictive observability forecast executions (ForecastRun)
and granular forecasted metric results (ForecastResult).
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
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
from app.models.enums import ForecastType, RiskLevel, TrendDirection

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class ForecastRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an execution of the Predictive Observability & Risk Forecasting Engine.
    """

    __tablename__ = "forecast_runs"

    __table_args__ = (
        Index("ix_forecast_runs_dataset_id", "dataset_id"),
        Index("ix_forecast_runs_forecast_type", "forecast_type"),
        Index("ix_forecast_runs_overall_risk_level", "overall_risk_level"),
        Index("ix_forecast_runs_created_at", "created_at"),
    )

    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    forecast_type: Mapped[ForecastType] = mapped_column(
        Enum(ForecastType, name="forecast_type", create_constraint=True),
        nullable=False,
    )
    algorithm_name: Mapped[str] = mapped_column(
        String(64),
        default="LinearRegression",
        nullable=False,
    )
    forecast_horizon_days: Mapped[int] = mapped_column(
        Integer,
        default=7,
        nullable=False,
    )
    overall_risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="forecast_risk_level", create_constraint=True),
        default=RiskLevel.LOW,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="completed",
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    results: Mapped[list["ForecastResult"]] = relationship(
        "ForecastResult",
        back_populates="forecast_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ForecastRun(id={self.id}, type='{self.forecast_type.value}', "
            f"risk='{self.overall_risk_level.value}')>"
        )


class ForecastResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an individual metric prediction datapoint with confidence bounds.
    """

    __tablename__ = "forecast_results"

    __table_args__ = (
        Index("ix_forecast_results_forecast_run_id", "forecast_run_id"),
        Index("ix_forecast_results_created_at", "created_at"),
    )

    forecast_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("forecast_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_metric: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    predicted_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    confidence_interval_lower: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    confidence_interval_upper: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    trend_direction: Mapped[TrendDirection] = mapped_column(
        Enum(TrendDirection, name="trend_direction", create_constraint=True),
        default=TrendDirection.STABLE,
        nullable=False,
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="result_risk_level", create_constraint=True),
        default=RiskLevel.LOW,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    preventive_actions: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    forecast_run: Mapped["ForecastRun"] = relationship("ForecastRun", back_populates="results")

    def __repr__(self) -> str:
        return f"<ForecastResult(id={self.id}, metric='{self.target_metric}', predicted={self.predicted_value:.2f})>"
