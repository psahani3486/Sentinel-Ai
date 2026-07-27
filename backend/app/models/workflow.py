"""
Sentinel AI — Workflow Orchestration Models

SQLAlchemy ORM models representing workflow execution pipelines (WorkflowRun)
and granular DAG step executions (WorkflowStepRun).
"""

import datetime
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
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
from app.models.enums import WorkflowState, WorkflowStepState, WorkflowType

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class WorkflowRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an execution pipeline run of a Sentinel AI workflow.
    """

    __tablename__ = "workflow_runs"

    __table_args__ = (
        Index("ix_workflow_runs_dataset_id", "dataset_id"),
        Index("ix_workflow_runs_workflow_type", "workflow_type"),
        Index("ix_workflow_runs_state", "state"),
        Index("ix_workflow_runs_created_at", "created_at"),
    )

    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    workflow_type: Mapped[WorkflowType] = mapped_column(
        Enum(WorkflowType, name="workflow_type", create_constraint=True),
        nullable=False,
    )
    state: Mapped[WorkflowState] = mapped_column(
        Enum(WorkflowState, name="workflow_state", create_constraint=True),
        default=WorkflowState.CREATED,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    total_steps: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    completed_steps: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    failed_steps: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    started_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    context_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    step_runs: Mapped[list["WorkflowStepRun"]] = relationship(
        "WorkflowStepRun",
        back_populates="workflow_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowRun(id={self.id}, type='{self.workflow_type.value}', "
            f"state='{self.state.value}')>"
        )


class WorkflowStepRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an execution of an individual step inside a workflow DAG.
    """

    __tablename__ = "workflow_step_runs"

    __table_args__ = (
        Index("ix_workflow_step_runs_workflow_run_id", "workflow_run_id"),
        Index("ix_workflow_step_runs_state", "state"),
        Index("ix_workflow_step_runs_created_at", "created_at"),
    )

    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    step_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    state: Mapped[WorkflowStepState] = mapped_column(
        Enum(WorkflowStepState, name="workflow_step_state", create_constraint=True),
        default=WorkflowStepState.PENDING,
        nullable=False,
    )
    depends_on: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )
    started_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    logs: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    outputs: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    workflow_run: Mapped["WorkflowRun"] = relationship("WorkflowRun", back_populates="step_runs")

    def __repr__(self) -> str:
        return f"<WorkflowStepRun(id={self.id}, name='{self.step_name}', state='{self.state.value}')>"
