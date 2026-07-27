"""
Sentinel AI — Base Incident Correlator Interface

Defines BaseIncidentCorrelator abstract strategy interface, IncidentContext,
RawTimelineEvent, and RawIncidentCandidate dataclasses.
"""

import abc
import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import IncidentEventType, IncidentSeverity, IncidentStatus


@dataclass
class RawTimelineEvent:
    """Dataclass holding an individual correlated timeline event."""

    timestamp: datetime.datetime
    event_type: IncidentEventType
    severity: IncidentSeverity
    description: str
    evidence_link: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentContext:
    """Telemetry context container supplied to incident correlators."""

    dataset_id: uuid.UUID | None = None
    title: str = "Unassigned Incident"
    severity: IncidentSeverity = IncidentSeverity.HIGH
    telemetry_signals: dict[str, Any] = field(default_factory=dict)


@dataclass
class RawIncidentCandidate:
    """Raw output candidate produced by incident correlators."""

    title: str
    severity: IncidentSeverity
    status: IncidentStatus
    summary: str
    root_cause_summary: str | None = None
    recommendations_summary: str | None = None
    forecast_summary: str | None = None
    timeline_events: list[RawTimelineEvent] = field(default_factory=list)
    related_datasets: list[str] = field(default_factory=list)
    related_jobs: list[str] = field(default_factory=list)
    related_alerts: list[str] = field(default_factory=list)


class BaseIncidentCorrelator(abc.ABC):
    """Abstract strategy interface for platform telemetry signal correlation."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Correlator identifier name."""
        pass

    @abc.abstractmethod
    def correlate(self, context: IncidentContext) -> list[RawTimelineEvent]:
        """
        Extract correlated timeline events from telemetry context.

        Args:
            context: IncidentContext containing multi-signal telemetry.

        Returns:
            List of RawTimelineEvent instances.
        """
        pass
