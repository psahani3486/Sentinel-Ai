"""
Sentinel AI — Background Job Queue Abstraction

Defines the pluggable QueueInterface contract and an async InMemoryQueue implementation.
Designed so Redis / Celery / RabbitMQ queues can be swapped without changing business logic.
"""

import abc
import asyncio
import uuid

from app.models.enums import JobPriority

PRIORITY_MAP = {
    JobPriority.CRITICAL: 1,
    JobPriority.HIGH: 2,
    JobPriority.MEDIUM: 3,
    JobPriority.LOW: 4,
}


class QueueInterface(abc.ABC):
    """Abstract interface defining standard job queue contract."""

    @abc.abstractmethod
    async def enqueue(self, job_id: uuid.UUID, priority: JobPriority = JobPriority.MEDIUM) -> None:
        """Add a job ID to the execution queue."""
        pass

    @abc.abstractmethod
    async def dequeue(self) -> uuid.UUID | None:
        """Fetch and remove the next priority job ID from the queue."""
        pass

    @abc.abstractmethod
    async def peek(self) -> uuid.UUID | None:
        """View the next priority job ID without removing it from the queue."""
        pass

    @abc.abstractmethod
    async def size(self) -> int:
        """Return total number of queued jobs."""
        pass

    @abc.abstractmethod
    async def clear(self) -> None:
        """Clear all queued jobs."""
        pass


class InMemoryQueue(QueueInterface):
    """
    In-memory priority job queue implementation.

    Uses an asyncio.PriorityQueue to maintain priority ordering (CRITICAL > HIGH > MEDIUM > LOW)
    with thread-safe non-blocking I/O.
    """

    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[tuple[int, float, uuid.UUID]] = asyncio.PriorityQueue()
        self._counter = 0.0

    async def enqueue(self, job_id: uuid.UUID, priority: JobPriority = JobPriority.MEDIUM) -> None:
        p_val = PRIORITY_MAP.get(priority, 3)
        self._counter += 1.0
        # PriorityQueue pops lowest priority integer first -> (1=CRITICAL, 2=HIGH, etc.)
        await self._queue.put((p_val, self._counter, job_id))

    async def dequeue(self) -> uuid.UUID | None:
        if self._queue.empty():
            return None
        _, _, job_id = await self._queue.get()
        return job_id

    async def peek(self) -> uuid.UUID | None:
        if self._queue.empty():
            return None
        # Access internal queue without mutating
        p_val, count_val, job_id = self._queue._queue[0]
        return job_id

    async def size(self) -> int:
        return self._queue.qsize()

    async def clear(self) -> None:
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break
