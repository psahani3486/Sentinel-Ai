"""
Sentinel AI — Platform Event Data Models

Pydantic event models representing background job lifecycle transitions and real-time incident alerts.
"""

import datetime
import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import AlertSeverity, AlertStatus, AlertType, JobStatus, JobType


class JobEvent(BaseModel):
    """Base event model for background job progress telemetry."""

    job_id: uuid.UUID
    job_type: JobType
    status: JobStatus
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    latest_message: str | None = None
    execution_time_ms: float = 0.0
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    event_type: str = "job_event"
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobCreatedEvent(JobEvent):
    """Emitted when a new background job is created."""

    event_type: str = "job_created"


class JobQueuedEvent(JobEvent):
    """Emitted when a job is enqueued into background queue."""

    event_type: str = "job_queued"


class JobStartedEvent(JobEvent):
    """Emitted when a worker begins job execution."""

    event_type: str = "job_started"


class JobProgressUpdatedEvent(JobEvent):
    """Emitted when job execution updates progress percentage or telemetry message."""

    event_type: str = "job_progress_updated"


class JobCompletedEvent(JobEvent):
    """Emitted when a job completes execution successfully."""

    event_type: str = "job_completed"


class JobFailedEvent(JobEvent):
    """Emitted when job execution fails."""

    error_message: str | None = None
    event_type: str = "job_failed"


class JobCancelledEvent(JobEvent):
    """Emitted when a job execution is cancelled."""

    event_type: str = "job_cancelled"


class AlertEvent(BaseModel):
    """Base event model for real-time incident alert telemetry."""

    alert_id: uuid.UUID
    alert_type: AlertType
    status: AlertStatus
    severity: AlertSeverity
    title: str
    description: str
    occurrence_count: int = 1
    dataset_id: uuid.UUID | None = None
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    event_type: str = "alert_event"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertCreatedEvent(AlertEvent):
    """Emitted when a new incident alert is created."""

    event_type: str = "alert_created"


class AlertUpdatedEvent(AlertEvent):
    """Emitted when an incident alert status or severity escalates."""

    event_type: str = "alert_updated"
