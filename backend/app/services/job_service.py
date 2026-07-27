"""
Sentinel AI — Job Service

Service layer managing job lifecycles (creation, queuing, progress tracking,
retries, cancellations, failures, and completions), dispatching via QueueInterface & JobExecutor,
and publishing real-time telemetry events via EventBusInterface.
"""

import datetime
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.events.event_bus import EventBusInterface, get_event_bus
from app.events.events import (
    JobCancelledEvent,
    JobCompletedEvent,
    JobCreatedEvent,
    JobFailedEvent,
    JobProgressUpdatedEvent,
    JobQueuedEvent,
    JobStartedEvent,
)
from app.jobs.executor import JobExecutor
from app.jobs.queue import InMemoryQueue, QueueInterface
from app.models.enums import JobPriority, JobStatus, JobType
from app.models.job import Job
from app.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)


def _ensure_utc(dt: datetime.datetime) -> datetime.datetime:
    """Ensure datetime object is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


class JobService:
    """Coordinates background job state machine, queue scheduling, execution, and real-time event publishing."""

    def __init__(
        self,
        job_repository: JobRepository | None = None,
        queue: QueueInterface | None = None,
        executor: JobExecutor | None = None,
        event_bus: EventBusInterface | None = None,
    ) -> None:
        self._repo = job_repository
        self._queue = queue or InMemoryQueue()
        self._executor = executor or JobExecutor()
        self._event_bus = event_bus or get_event_bus()

    async def create_job(
        self,
        job_type: JobType,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
        priority: JobPriority = JobPriority.MEDIUM,
        created_by_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> Job:
        """Create a new Job entity in PENDING status and publish JobCreatedEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository for persistence")

        job = Job(
            job_type=job_type,
            status=JobStatus.PENDING,
            priority=priority,
            progress_percentage=0.0,
            latest_message="Job created",
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            created_by_id=created_by_id,
            job_metadata=metadata or {},
            max_retries=max_retries,
        )
        job = await self._repo.create(job)
        logger.info("Created Job '%s' -> Type: %s, Priority: %s", job.id, job_type.value, priority.value)

        await self._event_bus.publish(
            JobCreatedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def queue_job(self, job_id: uuid.UUID) -> Job:
        """Enqueue a job for background processing and publish JobQueuedEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        job = await self._repo.update(
            job,
            {
                "status": JobStatus.QUEUED,
                "latest_message": "Job enqueued for background processing",
            },
        )
        await self._queue.enqueue(job.id, job.priority)
        logger.info("Queued Job '%s'", job.id)

        await self._event_bus.publish(
            JobQueuedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def start_job(self, job_id: uuid.UUID) -> Job:
        """Transition job status to RUNNING and publish JobStartedEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        now = datetime.datetime.now(datetime.timezone.utc)
        job = await self._repo.update(
            job,
            {
                "status": JobStatus.RUNNING,
                "started_at": now,
                "latest_message": "Job execution started",
            },
        )

        await self._event_bus.publish(
            JobStartedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def update_progress(
        self, job_id: uuid.UUID, progress_percentage: float, message: str | None = None
    ) -> Job:
        """Update job progress percentage (0-100), status message, and publish JobProgressUpdatedEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        update_dict: dict[str, Any] = {
            "progress_percentage": max(0.0, min(100.0, progress_percentage)),
        }
        if message:
            update_dict["latest_message"] = message

        job = await self._repo.update(job, update_dict)

        await self._event_bus.publish(
            JobProgressUpdatedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                execution_time_ms=job.execution_time_ms,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def complete_job(
        self, job_id: uuid.UUID, result_metadata: dict[str, Any] | None = None
    ) -> Job:
        """Mark job execution as COMPLETED and publish JobCompletedEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        now = datetime.datetime.now(datetime.timezone.utc)
        exec_ms = 0.0
        if job.started_at:
            started = _ensure_utc(job.started_at)
            exec_ms = round((now - started).total_seconds() * 1000, 2)

        merged_meta = dict(job.job_metadata or {})
        if result_metadata:
            merged_meta.update(result_metadata)

        val_run_id = job.validation_run_id
        if result_metadata and "validation_run_id" in result_metadata:
            try:
                val_run_id = uuid.UUID(result_metadata["validation_run_id"])
            except (ValueError, TypeError):
                pass

        job = await self._repo.update(
            job,
            {
                "status": JobStatus.COMPLETED,
                "progress_percentage": 100.0,
                "completed_at": now,
                "execution_time_ms": exec_ms,
                "latest_message": "Job execution completed successfully",
                "validation_run_id": val_run_id,
                "job_metadata": merged_meta,
            },
        )

        await self._event_bus.publish(
            JobCompletedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                execution_time_ms=job.execution_time_ms,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def fail_job(self, job_id: uuid.UUID, error_message: str) -> Job:
        """Mark job execution as FAILED and publish JobFailedEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        now = datetime.datetime.now(datetime.timezone.utc)
        exec_ms = 0.0
        if job.started_at:
            started = _ensure_utc(job.started_at)
            exec_ms = round((now - started).total_seconds() * 1000, 2)

        logger.error("Job '%s' failed: %s", job.id, error_message)
        job = await self._repo.update(
            job,
            {
                "status": JobStatus.FAILED,
                "completed_at": now,
                "execution_time_ms": exec_ms,
                "error_message": error_message,
                "latest_message": f"Job failed: {error_message}",
            },
        )

        await self._event_bus.publish(
            JobFailedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                execution_time_ms=job.execution_time_ms,
                error_message=error_message,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def cancel_job(self, job_id: uuid.UUID) -> Job:
        """Cancel an in-progress or queued job and publish JobCancelledEvent."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        now = datetime.datetime.now(datetime.timezone.utc)
        logger.info("Cancelled Job '%s'", job.id)
        job = await self._repo.update(
            job,
            {
                "status": JobStatus.CANCELLED,
                "completed_at": now,
                "latest_message": "Job execution cancelled by user",
            },
        )

        await self._event_bus.publish(
            JobCancelledEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                execution_time_ms=job.execution_time_ms,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def retry_job(self, job_id: uuid.UUID) -> Job:
        """Re-enqueue a failed job if retry limit has not been reached."""
        if not self._repo:
            raise ValueError("JobService requires JobRepository")

        job = await self._repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")

        if job.retry_count >= job.max_retries:
            raise ValueError(f"Job '{job_id}' exceeded maximum retries ({job.max_retries})")

        job = await self._repo.update(
            job,
            {
                "status": JobStatus.QUEUED,
                "retry_count": job.retry_count + 1,
                "error_message": None,
                "started_at": None,
                "completed_at": None,
                "progress_percentage": 0.0,
                "latest_message": f"Job retried (Attempt {job.retry_count + 1}/{job.max_retries})",
            },
        )
        await self._queue.enqueue(job.id, job.priority)
        await self._event_bus.publish(
            JobQueuedEvent(
                job_id=job.id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                latest_message=job.latest_message,
                metadata=job.job_metadata or {},
            )
        )
        return job

    async def process_next_job(self, db: AsyncSession) -> Job | None:
        """
        Pop the next job from queue, execute via JobExecutor, and update state.

        Returns:
            Processed Job ORM instance, or None if queue was empty.
        """
        job_id = await self._queue.dequeue()
        if not job_id:
            return None

        job = await self.start_job(job_id)
        try:
            await self.update_progress(job.id, 25.0, "Executing job payload...")
            res_meta = await self._executor.execute(job, db)
            await self.update_progress(job.id, 75.0, "Finalizing job payload...")
            completed_job = await self.complete_job(job.id, result_metadata=res_meta)
            return completed_job
        except Exception as e:
            failed_job = await self.fail_job(job.id, str(e))
            if failed_job.retry_count < failed_job.max_retries:
                try:
                    return await self.retry_job(failed_job.id)
                except Exception:
                    pass
            return failed_job
