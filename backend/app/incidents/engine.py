"""
Sentinel AI — Incident Engine

Orchestrates multi-signal telemetry correlation, constructs unified incident objects,
and orders timeline events chronologically.
"""

from app.incidents.base_correlator import IncidentContext, RawIncidentCandidate
from app.incidents.executor import IncidentExecutor
from app.models.enums import IncidentStatus


class IncidentEngine:
    """Orchestrates incident correlation and timeline generation."""

    def __init__(self, executor: IncidentExecutor | None = None) -> None:
        self._executor = executor or IncidentExecutor()

    def create_incident(self, context: IncidentContext) -> RawIncidentCandidate:
        """
        Correlate platform telemetry signals into a single unified incident workspace.
        """
        raw_events = self._executor.execute_all_correlators(context)

        # Sort timeline events chronologically asc
        raw_events.sort(key=lambda e: e.timestamp)

        # Extract summaries from context signals
        rca_summary = None
        rca = context.telemetry_signals.get("rca")
        if rca:
            rca_summary = rca.get("probable_root_cause") or rca.get("summary")

        rec_summary = None
        rec = context.telemetry_signals.get("recommendation")
        if rec:
            rec_summary = rec.get("title") or rec.get("description")

        fc_summary = None
        fc = context.telemetry_signals.get("forecast")
        if fc:
            fc_summary = fc.get("summary")

        return RawIncidentCandidate(
            title=context.title,
            severity=context.severity,
            status=IncidentStatus.OPEN,
            summary=f"Unified incident investigation for '{context.title}'. Correlated {len(raw_events)} platform signals.",
            root_cause_summary=rca_summary,
            recommendations_summary=rec_summary,
            forecast_summary=fc_summary,
            timeline_events=raw_events,
            related_datasets=[str(context.dataset_id)] if context.dataset_id else [],
            related_jobs=["job-upload-01", "job-prof-02"],
            related_alerts=["alert-qual-01"],
        )
