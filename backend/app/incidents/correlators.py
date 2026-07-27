"""
Sentinel AI — Automated Telemetry Signal Correlators

Implements signal correlator strategies:
1. Validation Correlator
2. Drift Correlator
3. Schema Correlator
4. Alert Correlator
5. AI Analysis Correlator (RCA, Recommendations, Forecasts)
"""

import datetime
from app.incidents.base_correlator import (
    BaseIncidentCorrelator,
    IncidentContext,
    RawTimelineEvent,
)
from app.models.enums import IncidentEventType, IncidentSeverity


# ── 1. Validation Correlator ───────────────────────────────────────────────────
class ValidationIncidentCorrelator(BaseIncidentCorrelator):
    @property
    def name(self) -> str:
        return "ValidationIncidentCorrelator"

    def correlate(self, context: IncidentContext) -> list[RawTimelineEvent]:
        events = []
        val_data = context.telemetry_signals.get("validation_results", [])
        now = datetime.datetime.now(datetime.timezone.utc)

        for idx, item in enumerate(val_data):
            t_offset = now - datetime.timedelta(minutes=30 - (idx * 5))
            events.append(
                RawTimelineEvent(
                    timestamp=t_offset,
                    event_type=IncidentEventType.VALIDATION_FAILED,
                    severity=IncidentSeverity.HIGH,
                    description=f"Validation rule '{item.get('rule_type', 'contract')}' failed on column '{item.get('column_name', 'dataset')}': {item.get('message', 'Validation rule error')}.",
                    evidence_link=f"/validations/{item.get('run_id', 'latest')}",
                    payload=item,
                )
            )
        return events


# ── 2. Drift Correlator ────────────────────────────────────────────────────────
class DriftIncidentCorrelator(BaseIncidentCorrelator):
    @property
    def name(self) -> str:
        return "DriftIncidentCorrelator"

    def correlate(self, context: IncidentContext) -> list[RawTimelineEvent]:
        events = []
        drift_data = context.telemetry_signals.get("drift_results", [])
        now = datetime.datetime.now(datetime.timezone.utc)

        for item in drift_data:
            events.append(
                RawTimelineEvent(
                    timestamp=now - datetime.timedelta(minutes=20),
                    event_type=IncidentEventType.DRIFT_DETECTED,
                    severity=IncidentSeverity.MEDIUM,
                    description=f"Feature distribution drift detected on feature '{item.get('feature_name', 'sensor_temp')}'. PSI: {item.get('psi_value', 0.18):.2f}.",
                    evidence_link="/drift",
                    payload=item,
                )
            )
        return events


# ── 3. Schema Correlator ───────────────────────────────────────────────────────
class SchemaIncidentCorrelator(BaseIncidentCorrelator):
    @property
    def name(self) -> str:
        return "SchemaIncidentCorrelator"

    def correlate(self, context: IncidentContext) -> list[RawTimelineEvent]:
        events = []
        schema_data = context.telemetry_signals.get("schema_changes", [])
        now = datetime.datetime.now(datetime.timezone.utc)

        for item in schema_data:
            events.append(
                RawTimelineEvent(
                    timestamp=now - datetime.timedelta(minutes=45),
                    event_type=IncidentEventType.SCHEMA_CHANGED,
                    severity=IncidentSeverity.HIGH,
                    description=f"Database schema change detected: {item.get('change_description', 'Column addition/modification')}.",
                    evidence_link="/datasets",
                    payload=item,
                )
            )
        return events


# ── 4. Alert Correlator ────────────────────────────────────────────────────────
class AlertIncidentCorrelator(BaseIncidentCorrelator):
    @property
    def name(self) -> str:
        return "AlertIncidentCorrelator"

    def correlate(self, context: IncidentContext) -> list[RawTimelineEvent]:
        events = []
        alerts_data = context.telemetry_signals.get("alerts", [])
        now = datetime.datetime.now(datetime.timezone.utc)

        for item in alerts_data:
            events.append(
                RawTimelineEvent(
                    timestamp=now - datetime.timedelta(minutes=15),
                    event_type=IncidentEventType.ALERT_TRIGGERED,
                    severity=IncidentSeverity.CRITICAL,
                    description=f"Incident alert triggered: {item.get('title', 'Platform SLA Breach')}.",
                    evidence_link=f"/alerts/{item.get('id', '1')}",
                    payload=item,
                )
            )
        return events


# ── 5. AI Analysis Correlator (RCA, Recommendations, Forecasts) ──────────────
class AIAnalysisIncidentCorrelator(BaseIncidentCorrelator):
    @property
    def name(self) -> str:
        return "AIAnalysisIncidentCorrelator"

    def correlate(self, context: IncidentContext) -> list[RawTimelineEvent]:
        events = []
        now = datetime.datetime.now(datetime.timezone.utc)

        # RCA
        rca = context.telemetry_signals.get("rca")
        if rca:
            events.append(
                RawTimelineEvent(
                    timestamp=now - datetime.timedelta(minutes=10),
                    event_type=IncidentEventType.RCA_COMPLETED,
                    severity=IncidentSeverity.INFO,
                    description=f"AI Root Cause Analysis completed: {rca.get('summary', 'Probable root cause isolated.')}",
                    evidence_link=f"/analysis/{rca.get('id', 'latest')}",
                    payload=rca,
                )
            )

        # Recommendation
        rec = context.telemetry_signals.get("recommendation")
        if rec:
            events.append(
                RawTimelineEvent(
                    timestamp=now - datetime.timedelta(minutes=5),
                    event_type=IncidentEventType.RECOMMENDATION_GENERATED,
                    severity=IncidentSeverity.INFO,
                    description=f"Actionable remediation recommendation generated: {rec.get('title', 'Remediation plan available.')}",
                    evidence_link=f"/recommendations/{rec.get('id', 'latest')}",
                    payload=rec,
                )
            )

        # Forecast
        fc = context.telemetry_signals.get("forecast")
        if fc:
            events.append(
                RawTimelineEvent(
                    timestamp=now - datetime.timedelta(minutes=2),
                    event_type=IncidentEventType.FORECAST_ALERT,
                    severity=IncidentSeverity.MEDIUM,
                    description=f"Predictive risk forecast generated: {fc.get('summary', 'Quality drop risk estimated.')}",
                    evidence_link=f"/forecast/{fc.get('id', 'latest')}",
                    payload=fc,
                )
            )

        return events
