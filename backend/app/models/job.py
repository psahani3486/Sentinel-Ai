"""
Sentinel AI — Background Job Model

Represents an asynchronous background job execution for dataset ingestion, profiling,
and validation workflows. Tracks status, progress, execution metrics, and retries.
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
from app.models.enums import JobPriority, JobStatus, JobType

if TYPE_CHECKING:
    from app.models.dataset import Dataset, DatasetVersion
    from app.models.user import User
    from app.models.validation import ValidationRun


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Background job execution entity.

    Tracks asynchronous execution lifecycle, progress percentage, execution duration,
    and associated dataset/validation run entities.
    """

    __tablename__ = "jobs"

    __table_args__ = (
        Index("ix_jobs_job_type", "job_type"),
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_priority", "priority"),
        Index("ix_jobs_dataset_id", "dataset_id"),
        Index("ix_jobs_created_at", "created_at"),
    )

    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="job_type", create_constraint=True),
        nullable=False,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", create_constraint=True),
        default=JobStatus.PENDING,
        nullable=False,
    )
    priority: Mapped[JobPriority] = mapped_column(
        Enum(JobPriority, name="job_priority", create_constraint=True),
        default=JobPriority.MEDIUM,
        nullable=False,
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    latest_message: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=True,
    )
    dataset_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=True,
    )
    validation_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("validation_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
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
    error_message: Mapped[str | None] = mapped_column(
        Text,
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
    job_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    dataset: Mapped["Dataset | None"] = relationship("Dataset")
    version: Mapped["DatasetVersion | None"] = relationship("DatasetVersion")
    validation_run: Mapped["ValidationRun | None"] = relationship("ValidationRun")
    created_by: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<Job(id={self.id}, type={self.job_type.value}, status={self.status.value}, "
            f"progress={self.progress_percentage:.1f}%)>"
        )
