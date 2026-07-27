"""
Sentinel AI — Incident Executor

Executes registered correlator strategies against multi-signal telemetry context.
"""

from app.incidents.base_correlator import IncidentContext, RawTimelineEvent
from app.incidents.registry import IncidentRegistry, get_incident_registry


class IncidentExecutor:
    """Executes all registered correlators to gather correlated timeline events."""

    def __init__(self, registry: IncidentRegistry | None = None) -> None:
        self._registry = registry or get_incident_registry()

    def execute_all_correlators(self, context: IncidentContext) -> list[RawTimelineEvent]:
        """
        Execute all registered correlators and collect timeline events.

        Returns:
            List of RawTimelineEvent instances.
        """
        all_events: list[RawTimelineEvent] = []
        for correlator in self._registry.get_all():
            events = correlator.correlate(context)
            all_events.extend(events)
        return all_events
