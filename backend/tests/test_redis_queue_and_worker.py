"""
Sentinel AI — Phase 3B Redis Queue & Worker Test Suite

Tests RedisQueue ZSET score calculation, atomic enqueue/dequeue/peek/size operations,
Worker polling loop, exponential backoff delays, graceful shutdown, and failure recovery.
"""

import asyncio
import uuid
import pytest
from unittest.mock import AsyncMock, patch

from app.jobs.executor import JobExecutor
from app.jobs.queue import InMemoryQueue
from app.jobs.redis_queue import RedisQueue, calculate_zset_score
from app.jobs.worker import Worker, get_exponential_backoff_seconds
from app.models.enums import JobPriority, JobStatus, JobType
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


def test_zset_score_calculation():
    """Test deterministic ZSET score calculation for priority ordering."""
    ts = 1700000000.0
    score_crit = calculate_zset_score(JobPriority.CRITICAL, timestamp=ts)
    score_high = calculate_zset_score(JobPriority.HIGH, timestamp=ts)
    score_med = calculate_zset_score(JobPriority.MEDIUM, timestamp=ts)
    score_low = calculate_zset_score(JobPriority.LOW, timestamp=ts)

    # Lower score pops first in Redis ZRANGE
    assert score_crit < score_high < score_med < score_low

    # Test FIFO ordering within same priority
    score_early = calculate_zset_score(JobPriority.HIGH, timestamp=ts)
    score_later = calculate_zset_score(JobPriority.HIGH, timestamp=ts + 10.0)
    assert score_early < score_later


def test_exponential_backoff_schedule():
    """Test exponential backoff delay schedule per retry attempt."""
    assert get_exponential_backoff_seconds(0) == 0.0
    assert get_exponential_backoff_seconds(1) == 5.0
    assert get_exponential_backoff_seconds(2) == 15.0
    assert get_exponential_backoff_seconds(3) == 30.0
    assert get_exponential_backoff_seconds(10) == 30.0  # Max delay cap
    assert get_exponential_backoff_seconds(-1) == 0.0


@pytest.mark.asyncio
async def test_redis_queue_mocked_zset_operations():
    """Test RedisQueue enqueue, dequeue, peek, size, and clear using mocked AsyncRedis client."""
    mock_redis = AsyncMock()
    mock_redis.zadd = AsyncMock()
    mock_redis.zrange = AsyncMock(side_effect=[["11111111-1111-1111-1111-111111111111"], ["11111111-1111-1111-1111-111111111111"], []])
    mock_redis.zrem = AsyncMock(return_value=1)
    mock_redis.zcard = AsyncMock(return_value=1)
    mock_redis.delete = AsyncMock()

    q = RedisQueue(redis_client=mock_redis, queue_name="test_sentinel_jobs")

    id1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
    await q.enqueue(id1, priority=JobPriority.CRITICAL)
    mock_redis.zadd.assert_called_once()

    peeked = await q.peek()
    assert peeked == id1

    dequeued = await q.dequeue()
    assert dequeued == id1

    sz = await q.size()
    assert sz == 1

    await q.clear()
    mock_redis.delete.assert_called_once_with("test_sentinel_jobs")
    await q.close()


@pytest.mark.asyncio
async def test_worker_polling_lifecycle_and_shutdown():
    """Test Worker polling loop startup, job dequeuing, execution, and graceful stop."""
    queue = InMemoryQueue()
    executor = JobExecutor()

    worker = Worker(queue=queue, executor=executor, poll_interval=0.01)

    id1 = uuid.uuid4()
    await queue.enqueue(id1, JobPriority.HIGH)

    # Mock _process_job_with_backoff to avoid database requirement in worker loop test
    with patch.object(worker, "_process_job_with_backoff", new_callable=AsyncMock) as mock_proc:
        task = asyncio.create_task(worker.start())
        await asyncio.sleep(0.05)
        worker.stop()
        await task

        mock_proc.assert_called_once()
        assert await queue.size() == 0


@pytest.mark.asyncio
async def test_worker_process_job_with_backoff_success(db_session, test_user):
    """Test Worker processing a job through start -> execute -> complete state machine."""
    job_repo = JobRepository(db_session)
    queue = InMemoryQueue()
    executor = JobExecutor()

    job_service = JobService(job_repository=job_repo, queue=queue, executor=executor)
    worker = Worker(queue=queue, executor=executor)

    job = await job_service.create_job(
        job_type=JobType.DATA_PROFILING,
        created_by_id=test_user.id,
    )

    with patch.object(executor, "execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"profile_id": "test_profile_123"}

        await worker._process_job_with_backoff(job.id, job_service, db_session)

        updated_job = await job_repo.get_by_id(job.id)
        assert updated_job.status == JobStatus.COMPLETED
        assert updated_job.progress_percentage == 100.0
        assert updated_job.job_metadata.get("profile_id") == "test_profile_123"


@pytest.mark.asyncio
async def test_worker_failure_and_backoff_retry(db_session, test_user):
    """Test Worker handling job execution failure and scheduling auto-retry."""
    job_repo = JobRepository(db_session)
    queue = InMemoryQueue()
    executor = JobExecutor()

    job_service = JobService(job_repository=job_repo, queue=queue, executor=executor)
    worker = Worker(queue=queue, executor=executor)

    job = await job_service.create_job(
        job_type=JobType.DATA_PROFILING,
        created_by_id=test_user.id,
        max_retries=2,
    )

    with patch.object(executor, "execute", side_effect=ValueError("Simulated Executor Failure")):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            await worker._process_job_with_backoff(job.id, job_service, db_session)

            updated_job = await job_repo.get_by_id(job.id)
            assert updated_job.status == JobStatus.QUEUED
            assert updated_job.retry_count == 1
            assert await queue.size() == 1
