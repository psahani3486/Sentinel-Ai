"""
Sentinel AI — Base Alert Rule Strategy

Defines BaseAlertRule abstract strategy interface and AlertCandidate dataclass.
"""

import abc
import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import AlertSeverity, AlertType


@dataclass
class AlertCandidate:
    """Standardized output produced by an Alert Rule evaluation."""

    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    dataset_id: uuid.UUID | None = None
    target_entity_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def generate_fingerprint(self) -> str:
        """
        Generate deterministic fingerprint hash for alert deduplication.
        Fingerprint = SHA256(dataset_id + alert_type + target_entity_id)
        """
        raw_key = f"{self.dataset_id or 'global'}:{self.alert_type.value}:{self.target_entity_id or 'default'}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class BaseAlertRule(abc.ABC):
    """Abstract strategy interface for automated platform incident alert rules."""

    @property
    @abc.abstractmethod
    def alert_type(self) -> AlertType:
        """Return the unique AlertType enum key."""
        pass

    @abc.abstractmethod
    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        """
        Evaluate an event payload against rule criteria.

        Args:
            event_payload: Telemetry dictionary from validation runs, jobs, drift runs, or pipeline events.

        Returns:
            AlertCandidate if rule condition is satisfied, otherwise None.
        """
        pass
