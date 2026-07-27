"""
Sentinel AI — Phase 3A Background Job System Test Suite

Tests Job lifecycle, queue enqueue/dequeue/priority ordering, JobExecutor,
JobService, repository database queries, auto-retry logic, and error handling.
"""

import os
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.executor import JobExecutor
from app.jobs.queue import InMemoryQueue
from app.models.dataset import Dataset, DatasetVersion
from app.models.enums import ConnectorType, DatasetType, JobPriority, JobStatus, JobType
from app.models.job import Job
from app.repositories.dataset_repository import DatasetRepository, DatasetVersionRepository
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


@pytest.mark.asyncio
async def test_queue_enqueue_dequeue_and_priority():
    """Test InMemoryQueue FIFO and Priority ordering (CRITICAL > HIGH > MEDIUM > LOW)."""
    queue = InMemoryQueue()
    assert await queue.size() == 0
    assert await queue.peek() is None
    assert await queue.dequeue() is None

    id_low = uuid.uuid4()
    id_critical = uuid.uuid4()
    id_high = uuid.uuid4()

    await queue.enqueue(id_low, priority=JobPriority.LOW)
    await queue.enqueue(id_critical, priority=JobPriority.CRITICAL)
    await queue.enqueue(id_high, priority=JobPriority.HIGH)

    assert await queue.size() == 3
    assert await queue.peek() == id_critical

    # Dequeue order should be CRITICAL -> HIGH -> LOW
    dequeued_1 = await queue.dequeue()
    assert dequeued_1 == id_critical

    dequeued_2 = await queue.dequeue()
    assert dequeued_2 == id_high

    dequeued_3 = await queue.dequeue()
    assert dequeued_3 == id_low

    assert await queue.size() == 0
    await queue.clear()


@pytest.mark.asyncio
async def test_job_repository_crud(db_session: AsyncSession, test_user):
    """Test JobRepository persistence, queries, and paginated filters."""
    job_repo = JobRepository(db_session)
    dataset_id = uuid.uuid4()

    job = Job(
        job_type=JobType.DATA_PROFILING,
        status=JobStatus.PENDING,
        priority=JobPriority.HIGH,
        progress_percentage=0.0,
        dataset_id=dataset_id,
        created_by_id=test_user.id,
    )
    job = await job_repo.create(job)
    assert job.id is not None
    assert job.status == JobStatus.PENDING

    fetched = await job_repo.get_by_id(job.id)
    assert fetched is not None
    assert fetched.priority == JobPriority.HIGH

    # Test get_pending_or_queued_jobs
    pending_jobs = await job_repo.get_pending_or_queued_jobs(limit=10)
    assert len(pending_jobs) >= 1
    assert any(j.id == job.id for j in pending_jobs)

    # Test get_jobs_by_status
    by_status_items, total = await job_repo.get_jobs_by_status(JobStatus.PENDING, limit=10)
    assert total >= 1
    assert any(j.id == job.id for j in by_status_items)

    # Test get_jobs_by_dataset
    by_dataset_items, ds_total = await job_repo.get_jobs_by_dataset(dataset_id, limit=10)
    assert ds_total == 1
    assert by_dataset_items[0].id == job.id

    # Update job status
    updated = await job_repo.update(job, {"status": JobStatus.RUNNING, "progress_percentage": 50.0})
    assert updated.status == JobStatus.RUNNING
    assert updated.progress_percentage == 50.0


@pytest.mark.asyncio
async def test_job_service_lifecycle_and_state_transitions(db_session: AsyncSession, test_user):
    """Test complete JobService state machine transitions (PENDING -> QUEUED -> RUNNING -> COMPLETED)."""
    job_repo = JobRepository(db_session)
    queue = InMemoryQueue()
    svc = JobService(job_repository=job_repo, queue=queue)

    # 1. Create Job
    job = await svc.create_job(
        job_type=JobType.DATA_PROFILING,
        priority=JobPriority.CRITICAL,
        created_by_id=test_user.id,
        metadata={"test": "payload"},
    )
    assert job.status == JobStatus.PENDING
    assert job.progress_percentage == 0.0

    # 2. Queue Job
    queued_job = await svc.queue_job(job.id)
    assert queued_job.status == JobStatus.QUEUED
    assert await queue.size() == 1

    # 3. Start Job
    running_job = await svc.start_job(job.id)
    assert running_job.status == JobStatus.RUNNING
    assert running_job.started_at is not None

    # 4. Progress Updates
    progress_job = await svc.update_progress(job.id, 45.0, "Analyzing statistics...")
    assert progress_job.progress_percentage == 45.0
    assert progress_job.latest_message == "Analyzing statistics..."

    # 5. Complete Job
    completed_job = await svc.complete_job(job.id, result_metadata={"rows": 100})
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.progress_percentage == 100.0
    assert completed_job.completed_at is not None
    assert completed_job.job_metadata.get("rows") == 100


@pytest.mark.asyncio
async def test_job_service_cancel_and_failure(db_session: AsyncSession, test_user):
    """Test job cancellation and failure state transitions."""
    job_repo = JobRepository(db_session)
    svc = JobService(job_repository=job_repo)

    job1 = await svc.create_job(job_type=JobType.DATA_VALIDATION, created_by_id=test_user.id)
    cancelled = await svc.cancel_job(job1.id)
    assert cancelled.status == JobStatus.CANCELLED
    assert "cancelled" in cancelled.latest_message.lower()

    job2 = await svc.create_job(job_type=JobType.DATASET_UPLOAD, created_by_id=test_user.id)
    failed = await svc.fail_job(job2.id, "Corrupted file payload")
    assert failed.status == JobStatus.FAILED
    assert failed.error_message == "Corrupted file payload"


@pytest.mark.asyncio
async def test_job_service_exceptions_handling(db_session: AsyncSession):
    """Test JobService error paths (missing repo / invalid job ID)."""
    svc_no_repo = JobService()
    dummy_id = uuid.uuid4()

    with pytest.raises(ValueError, match="JobService requires JobRepository"):
        await svc_no_repo.create_job(JobType.DATA_PROFILING)

    svc = JobService(job_repository=JobRepository(db_session))

    with pytest.raises(ValueError, match="not found"):
        await svc.queue_job(dummy_id)

    with pytest.raises(ValueError, match="not found"):
        await svc.start_job(dummy_id)

    with pytest.raises(ValueError, match="not found"):
        await svc.update_progress(dummy_id, 10.0)

    with pytest.raises(ValueError, match="not found"):
        await svc.complete_job(dummy_id)

    with pytest.raises(ValueError, match="not found"):
        await svc.fail_job(dummy_id, "error")

    with pytest.raises(ValueError, match="not found"):
        await svc.cancel_job(dummy_id)

    with pytest.raises(ValueError, match="not found"):
        await svc.retry_job(dummy_id)


@pytest.mark.asyncio
async def test_job_retry_logic(db_session: AsyncSession, test_user):
    """Test job retry mechanics and retry limit enforcement."""
    job_repo = JobRepository(db_session)
    queue = InMemoryQueue()
    svc = JobService(job_repository=job_repo, queue=queue)

    job = await svc.create_job(
        job_type=JobType.DATA_PROFILING,
        created_by_id=test_user.id,
        max_retries=2,
    )
    failed_job = await svc.fail_job(job.id, "Temporary network timeout")

    # Retry 1
    retried_1 = await svc.retry_job(failed_job.id)
    assert retried_1.status == JobStatus.QUEUED
    assert retried_1.retry_count == 1
    assert retried_1.error_message is None

    # Fail again and Retry 2
    failed_2 = await svc.fail_job(retried_1.id, "Second failure")
    retried_2 = await svc.retry_job(failed_2.id)
    assert retried_2.retry_count == 2

    # Fail again and exceed max retries
    failed_3 = await svc.fail_job(retried_2.id, "Third failure")
    with pytest.raises(ValueError, match="exceeded maximum retries"):
        await svc.retry_job(failed_3.id)


@pytest.mark.asyncio
async def test_full_job_execution_pipeline(db_session: AsyncSession, test_user):
    """Test full queue dispatching and execution for DATASET_UPLOAD, DATA_PROFILING & DATA_VALIDATION jobs."""
    dataset_repo = DatasetRepository(db_session)
    version_repo = DatasetVersionRepository(db_session)
    job_repo = JobRepository(db_session)
    queue = InMemoryQueue()

    executor = JobExecutor()
    svc = JobService(job_repository=job_repo, queue=queue, executor=executor)

    sample_csv = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "samples", "ai4i2020.csv"
    )

    dataset = Dataset(
        name="Job Execution Test Dataset",
        description="Dataset for job executor pipeline validation",
        dataset_type=DatasetType.SENSOR_STREAM,
        connector_type=ConnectorType.INDUSTRIAL_SENSOR,
        connection_config={"file_path": sample_csv},
        owner_id=test_user.id,
    )
    dataset = await dataset_repo.create(dataset)

    version = DatasetVersion(
        dataset_id=dataset.id,
        version_number=1,
        storage_path=sample_csv,
        ingested_by_id=test_user.id,
    )
    version = await version_repo.create(version)

    # 1. Dispatch DATASET_UPLOAD job
    upload_job = await svc.create_job(
        job_type=JobType.DATASET_UPLOAD,
        dataset_id=dataset.id,
        dataset_version_id=version.id,
        created_by_id=test_user.id,
        metadata={"file_path": sample_csv, "connector_type": "industrial_sensor"},
    )
    await svc.queue_job(upload_job.id)

    processed_upload = await svc.process_next_job(db_session)
    assert processed_upload is not None
    assert processed_upload.status == JobStatus.COMPLETED

    # 2. Dispatch DATA_PROFILING job
    prof_job = await svc.create_job(
        job_type=JobType.DATA_PROFILING,
        dataset_id=dataset.id,
        dataset_version_id=version.id,
        priority=JobPriority.HIGH,
        created_by_id=test_user.id,
    )
    await svc.queue_job(prof_job.id)

    processed_prof = await svc.process_next_job(db_session)
    assert processed_prof is not None
    assert processed_prof.status == JobStatus.COMPLETED
    assert processed_prof.progress_percentage == 100.0

    # 3. Dispatch DATA_VALIDATION job
    val_job = await svc.create_job(
        job_type=JobType.DATA_VALIDATION,
        dataset_id=dataset.id,
        dataset_version_id=version.id,
        priority=JobPriority.CRITICAL,
        created_by_id=test_user.id,
    )
    await svc.queue_job(val_job.id)

    processed_val = await svc.process_next_job(db_session)
    assert processed_val is not None
    assert processed_val.status == JobStatus.COMPLETED
    assert processed_val.validation_run_id is not None

    # 4. Test empty queue return
    assert await svc.process_next_job(db_session) is None


@pytest.mark.asyncio
async def test_executor_error_handling(db_session: AsyncSession):
    """Test JobExecutor validation & error handling for invalid/missing metadata."""
    executor = JobExecutor()

    job_invalid_type = Job(
        job_type="invalid_type",  # type: ignore
        job_metadata={},
    )
    with pytest.raises(ValueError, match="Unsupported job type"):
        await executor.execute(job_invalid_type, db_session)

    job_upload_missing_file = Job(
        job_type=JobType.DATASET_UPLOAD,
        job_metadata={"file_path": "non_existent_file.csv"},
    )
    with pytest.raises(FileNotFoundError, match="Target upload file not found"):
        await executor.execute(job_upload_missing_file, db_session)

    job_prof_missing_ver = Job(
        job_type=JobType.DATA_PROFILING,
        job_metadata={},
    )
    with pytest.raises(ValueError, match="DATA_PROFILING job requires dataset_version_id"):
        await executor.execute(job_prof_missing_ver, db_session)

    job_val_missing_ver = Job(
        job_type=JobType.DATA_VALIDATION,
        job_metadata={},
    )
    with pytest.raises(ValueError, match="DATA_VALIDATION job requires dataset_version_id"):
        await executor.execute(job_val_missing_ver, db_session)
