"""
Sentinel AI — Distributed Job Worker Process

Asynchronous background worker polling process that dequeues jobs, dispatches execution
via JobExecutor, enforces exponential backoff auto-retries, handles graceful shutdown signals,
and persists execution tracebacks.

Run worker CLI via:
    python -m app.jobs.worker
"""

import asyncio
import logging
import signal
from typing import Any

from app.config.settings import get_settings
from app.db.session import async_session_factory
from app.jobs.executor import JobExecutor
from app.jobs.queue import InMemoryQueue, QueueInterface
from app.jobs.redis_queue import RedisQueue
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService

logger = logging.getLogger(__name__)

# Exponential backoff delay schedule in seconds per retry attempt
BACKOFF_DELAYS = [0.0, 5.0, 15.0, 30.0]


def get_exponential_backoff_seconds(retry_count: int) -> float:
    """Calculate exponential backoff delay in seconds for a retry attempt."""
    if retry_count < 0:
        return 0.0
    if retry_count < len(BACKOFF_DELAYS):
        return BACKOFF_DELAYS[retry_count]
    return BACKOFF_DELAYS[-1]


class Worker:
    """
    Distributed Worker process managing continuous queue polling, execution,
    exponential backoff retries, and graceful shutdown signal handling.
    """

    def __init__(
        self,
        queue: QueueInterface | None = None,
        executor: JobExecutor | None = None,
        poll_interval: float | None = None,
    ) -> None:
        settings = get_settings()
        self._queue = queue
        self._executor = executor or JobExecutor()
        self._poll_interval = poll_interval or settings.WORKER_POLL_INTERVAL_SECONDS
        self._running = False
        self._active_job_count = 0

    def _init_queue(self) -> QueueInterface:
        if self._queue is None:
            try:
                self._queue = RedisQueue()
            except Exception as e:
                logger.warning("Redis queue unavailable (%s), falling back to InMemoryQueue", e)
                self._queue = InMemoryQueue()
        return self._queue

    def stop(self) -> None:
        """Signal worker to stop processing new jobs and gracefully exit."""
        logger.info("Worker shutdown signal received. Stopping worker loop...")
        self._running = False

    async def start(self) -> None:
        """Start the worker continuous polling loop."""
        self._running = True
        queue = self._init_queue()
        logger.info("Sentinel AI Worker started polling queue (Interval: %.1fs)", self._poll_interval)

        while self._running:
            try:
                async with async_session_factory() as db:
                    job_repo = JobRepository(db)
                    job_service = JobService(job_repository=job_repo, queue=queue, executor=self._executor)

                    job_id = await queue.dequeue()
                    if job_id:
                        self._active_job_count += 1
                        logger.info("Worker dequeued Job '%s'. Executing...", job_id)
                        await self._process_job_with_backoff(job_id, job_service, db)
                        self._active_job_count -= 1
                    else:
                        await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                logger.info("Worker task cancelled.")
                break
            except Exception as e:
                logger.error("Unexpected error in worker loop: %s", e, exc_info=True)
                await asyncio.sleep(self._poll_interval)

        logger.info("Worker loop terminated cleanly. Active jobs remaining: %d", self._active_job_count)

    async def _process_job_with_backoff(
        self, job_id: Any, job_service: JobService, db: Any
    ) -> None:
        """Process job with start state transition, execution, and exponential backoff retries."""
        try:
            job = await job_service.start_job(job_id)
            await job_service.update_progress(job.id, 25.0, "Worker executing job payload...")

            result = await self._executor.execute(job, db)

            await job_service.update_progress(job.id, 75.0, "Worker finalizing execution...")
            await job_service.complete_job(job.id, result_metadata=result)
            logger.info("Worker completed Job '%s' successfully.", job.id)
        except Exception as err:
            err_msg = str(err)
            logger.error("Job '%s' failed during worker execution: %s", job_id, err_msg)
            failed_job = await job_service.fail_job(job_id, err_msg)

            # Enforce exponential backoff auto-retry if retries remaining
            if failed_job.retry_count < failed_job.max_retries:
                delay = get_exponential_backoff_seconds(failed_job.retry_count)
                logger.info("Scheduling retry %d/%d for Job '%s' after %.1fs backoff",
                            failed_job.retry_count + 1, failed_job.max_retries, job_id, delay)
                if delay > 0:
                    await asyncio.sleep(delay)
                try:
                    await job_service.retry_job(job_id)
                except Exception as retry_err:
                    logger.error("Failed to schedule retry for Job '%s': %s", job_id, retry_err)


async def main_cli() -> None:
    """Worker CLI entrypoint registering signal handlers."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    worker = Worker()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, worker.stop)
        except NotImplementedError:
            # Signal handling not supported on Windows main thread loop in some modes
            pass

    try:
        await worker.start()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main_cli())
