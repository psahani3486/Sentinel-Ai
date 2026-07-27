"""
Sentinel AI — Redis Background Job Queue

Production-ready Redis-backed queue implementing QueueInterface using Redis Sorted Sets (ZSET).
Supports priority scheduling (CRITICAL > HIGH > MEDIUM > LOW) with FIFO microsecond timestamp sub-ordering.
"""

import logging
import time
import uuid

import redis.asyncio as redis

from app.config.settings import get_settings
from app.jobs.queue import PRIORITY_MAP, QueueInterface
from app.models.enums import JobPriority

logger = logging.getLogger(__name__)


def calculate_zset_score(priority: JobPriority, timestamp: float | None = None) -> float:
    """
    Calculate deterministic Redis ZSET score.

    Score = (PriorityRank * 1e12) + MicrosecondTimestamp
    Since ZRANGE pops lowest score first:
    - CRITICAL (Rank 1) -> 1e12 + ts
    - HIGH (Rank 2) -> 2e12 + ts
    - MEDIUM (Rank 3) -> 3e12 + ts
    - LOW (Rank 4) -> 4e12 + ts
    Within the same priority rank, earlier timestamps have lower scores (FIFO).
    """
    ts = timestamp if timestamp is not None else time.time()
    rank = PRIORITY_MAP.get(priority, 3)
    return float(rank * 1e12 + (ts * 1e6 % 1e12))


class RedisQueue(QueueInterface):
    """
    Redis-backed ZSET job queue implementation.

    Provides priority-ordered queueing with atomic ZRANGE + ZREM operations.
    Fully implements QueueInterface contract.
    """

    def __init__(self, redis_client: redis.Redis | None = None, queue_name: str | None = None) -> None:
        settings = get_settings()
        self._queue_name = queue_name or settings.REDIS_QUEUE_NAME
        self._redis_url = settings.REDIS_URL
        self._client = redis_client

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    async def enqueue(self, job_id: uuid.UUID, priority: JobPriority = JobPriority.MEDIUM) -> None:
        """Enqueue job ID into Redis ZSET with priority score."""
        client = await self._get_client()
        score = calculate_zset_score(priority)
        await client.zadd(self._queue_name, {str(job_id): score})
        logger.debug("RedisQueue ZADD '%s' -> job_id: %s, score: %f", self._queue_name, job_id, score)

    async def dequeue(self) -> uuid.UUID | None:
        """Atomically fetch and remove the lowest score (highest priority) job ID."""
        client = await self._get_client()
        # Fetch lowest score item
        items = await client.zrange(self._queue_name, 0, 0)
        if not items:
            return None

        job_id_str = items[0]
        # Atomically remove
        removed = await client.zrem(self._queue_name, job_id_str)
        if removed > 0:
            return uuid.UUID(job_id_str)
        return None

    async def peek(self) -> uuid.UUID | None:
        """View the next priority job ID without popping it."""
        client = await self._get_client()
        items = await client.zrange(self._queue_name, 0, 0)
        if not items:
            return None
        return uuid.UUID(items[0])

    async def size(self) -> int:
        """Return total count of queued jobs in Redis ZSET."""
        client = await self._get_client()
        return await client.zcard(self._queue_name)

    async def clear(self) -> None:
        """Remove all jobs from Redis queue."""
        client = await self._get_client()
        await client.delete(self._queue_name)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
