"""
Sentinel AI — EventBus Abstraction

Defines the pluggable EventBusInterface contract and an in-memory async InMemoryEventBus.
Designed so Redis Pub/Sub / Kafka event channels can be swapped without changing business logic.
"""

import abc
import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable

from app.events.events import JobEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[JobEvent], Awaitable[None]]


class EventBusInterface(abc.ABC):
    """Abstract interface for application event publishing and subscription."""

    @abc.abstractmethod
    async def publish(self, event: JobEvent) -> None:
        """Publish an event to all registered subscribers."""
        pass

    @abc.abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe an async handler callback to a specific event_type or '*' for all events."""
        pass

    @abc.abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe a handler callback."""
        pass


class InMemoryEventBus(EventBusInterface):
    """
    In-memory async pub/sub EventBus implementation.

    Dispatches events asynchronously to registered callback handlers without blocking execution.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, set[EventHandler]] = defaultdict(set)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].add(handler)
        logger.debug("Subscribed handler to event_type '%s'", event_type)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.debug("Unsubscribed handler from event_type '%s'", event_type)

    async def publish(self, event: JobEvent) -> None:
        """Publish event asynchronously to exact type subscribers and wildcard '*' subscribers."""
        handlers = list(self._subscribers.get(event.event_type, set()))
        wildcard_handlers = list(self._subscribers.get("*", set()))
        all_handlers = list(set(handlers + wildcard_handlers))

        if not all_handlers:
            return

        for handler in all_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error("Error executing event handler for event '%s': %s", event.event_type, e, exc_info=True)


# Application-wide global EventBus instance singleton
_global_event_bus: InMemoryEventBus | None = None


def get_event_bus() -> InMemoryEventBus:
    """Return application-wide EventBus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = InMemoryEventBus()
    return _global_event_bus
