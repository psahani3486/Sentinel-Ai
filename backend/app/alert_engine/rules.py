"""
Sentinel AI — Automated Alert Evaluation Rules

Implements 10 independent alert rules:
1. Quality Score Drop Alert
2. Validation Failure Alert
3. Critical Validation Rule Alert
4. Schema Change Alert
5. Data Drift Alert
6. Pipeline Failure Alert
7. Pipeline Timeout Alert
8. Job Failure Alert
9. Dataset Freshness Alert
10. Repeated Failure Alert
"""

import uuid
from typing import Any

from app.alert_engine.base_rule import AlertCandidate, BaseAlertRule
from app.models.enums import AlertSeverity, AlertType


# ── 1. Quality Score Drop Rule ────────────────────────────────────────────────
class QualityScoreDropRule(BaseAlertRule):
    """Triggers when data quality score drops below target SLA (default 85%)."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.QUALITY_SCORE_DROP

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        score = event_payload.get("quality_score")
        if score is None or not isinstance(score, (int, float)):
            return None

        threshold = event_payload.get("target_sla", 85.0)
        if score < threshold:
            sev = AlertSeverity.CRITICAL if score < 70.0 else AlertSeverity.HIGH
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=sev,
                title=f"Data Quality Score Drop ({score:.1f}%)",
                description=f"Quality score {score:.1f}% dropped below SLA target threshold {threshold:.1f}%.",
                dataset_id=parsed_id,
                target_entity_id=str(parsed_id or "global"),
                metadata={"quality_score": score, "target_sla": threshold},
            )
        return None


# ── 2. Validation Failure Rule ────────────────────────────────────────────────
class ValidationFailureRule(BaseAlertRule):
    """Triggers on validation run suite failure."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.VALIDATION_FAILURE

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        if event_payload.get("run_status") == "failed" or event_payload.get("event_type") == "validation_failed":
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            run_id = event_payload.get("validation_run_id", "suite")
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.HIGH,
                title="Data Validation Suite Failure",
                description=f"Validation run suite '{run_id}' failed execution rules.",
                dataset_id=parsed_id,
                target_entity_id=str(run_id),
                metadata=event_payload,
            )
        return None


# ── 3. Critical Validation Rule ───────────────────────────────────────────────
class CriticalValidationRule(BaseAlertRule):
    """Triggers when a CRITICAL severity validation rule breaks."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.CRITICAL_VALIDATION_RULE

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        crit_count = event_payload.get("failed_critical_rules_count", 0)
        if crit_count > 0 or event_payload.get("rule_severity") == "critical":
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            col = event_payload.get("column_name", "dataset")
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.CRITICAL,
                title=f"Critical Rule Violation on '{col}'",
                description=f"Detected {crit_count} critical rule violations impacting core pipeline SLAs.",
                dataset_id=parsed_id,
                target_entity_id=f"{ds_id}:{col}",
                metadata=event_payload,
            )
        return None


# ── 4. Schema Change Rule ─────────────────────────────────────────────────────
class SchemaChangeRule(BaseAlertRule):
    """Triggers on structural schema evolution (column added/deleted/type changed)."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.SCHEMA_CHANGE

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        if event_payload.get("event_type") == "schema_change" or event_payload.get("schema_modified", False):
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            changes = event_payload.get("schema_changes", "Column definitions modified")
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.MEDIUM,
                title="Structural Schema Change Detected",
                description=f"Dataset schema evolved: {changes}.",
                dataset_id=parsed_id,
                target_entity_id=str(parsed_id or "schema"),
                metadata=event_payload,
            )
        return None


# ── 5. Data Drift Rule ────────────────────────────────────────────────────────
class DataDriftRule(BaseAlertRule):
    """Triggers when feature data drift status is HIGH or CRITICAL."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.DATA_DRIFT

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        status = str(event_payload.get("drift_status", "")).lower()
        if status in ("high", "critical"):
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            score = event_payload.get("overall_drift_score", 0.0)
            sev = AlertSeverity.CRITICAL if status == "critical" else AlertSeverity.HIGH
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=sev,
                title=f"Feature Data Drift Detected ({status.upper()})",
                description=f"Dataset overall drift index reached {score:.1f}% ({status.upper()} threshold).",
                dataset_id=parsed_id,
                target_entity_id=str(parsed_id or "drift"),
                metadata=event_payload,
            )
        return None


# ── 6. Pipeline Failure Rule ──────────────────────────────────────────────────
class PipelineFailureRule(BaseAlertRule):
    """Triggers on ingestion pipeline / connector execution failure."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.PIPELINE_FAILURE

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        if event_payload.get("pipeline_status") == "failed" or event_payload.get("connector_failed", False):
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            conn = event_payload.get("connector_name", "Ingestion Pipeline")
            err = event_payload.get("error_message", "Connector disconnected")
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.HIGH,
                title=f"Pipeline Failure: {conn}",
                description=f"Data ingestion pipeline failed: {err}.",
                dataset_id=parsed_id,
                target_entity_id=f"{conn}:{ds_id}",
                metadata=event_payload,
            )
        return None


# ── 7. Pipeline Timeout Rule ──────────────────────────────────────────────────
class PipelineTimeoutRule(BaseAlertRule):
    """Triggers when pipeline execution duration exceeds SLA timeout (5 minutes)."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.PIPELINE_TIMEOUT

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        exec_ms = event_payload.get("execution_time_ms", 0.0)
        timeout_ms = event_payload.get("timeout_limit_ms", 300000.0)  # 5 mins
        if exec_ms > timeout_ms or event_payload.get("timed_out", False):
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            mins = exec_ms / 60000.0
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.MEDIUM,
                title="Pipeline Execution Timeout SLA Exceeded",
                description=f"Pipeline execution took {mins:.1f} minutes, exceeding SLA timeout limit.",
                dataset_id=parsed_id,
                target_entity_id=str(parsed_id or "timeout"),
                metadata=event_payload,
            )
        return None


# ── 8. Job Failure Rule ───────────────────────────────────────────────────────
class JobFailureRule(BaseAlertRule):
    """Triggers when a background worker job transitions to FAILED."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.JOB_FAILURE

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        if event_payload.get("event_type") == "job_failed" or event_payload.get("job_status") == "failed":
            job_id = event_payload.get("job_id")
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            err = event_payload.get("error_message", "Worker task exception")
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.HIGH,
                title="Background Worker Job Execution Failure",
                description=f"Background job '{job_id}' failed: {err}.",
                dataset_id=parsed_id,
                target_entity_id=str(job_id or "job"),
                metadata=event_payload,
            )
        return None


# ── 9. Dataset Freshness Rule ─────────────────────────────────────────────────
class DatasetFreshnessRule(BaseAlertRule):
    """Triggers when dataset ingestion freshness exceeds threshold (> 24 hours)."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.DATASET_FRESHNESS

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        hours = event_payload.get("hours_since_last_ingest", 0.0)
        threshold_hours = event_payload.get("freshness_sla_hours", 24.0)
        if hours > threshold_hours or event_payload.get("stale_data", False):
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.MEDIUM,
                title="Stale Dataset Freshness Alert",
                description=f"Dataset has not received new data in {hours:.1f} hours (SLA limit: {threshold_hours:.0f}h).",
                dataset_id=parsed_id,
                target_entity_id=str(parsed_id or "freshness"),
                metadata=event_payload,
            )
        return None


# ── 10. Repeated Failure Rule ─────────────────────────────────────────────────
class RepeatedFailureRule(BaseAlertRule):
    """Triggers when multiple consecutive failures occur on the same target entity."""

    @property
    def alert_type(self) -> AlertType:
        return AlertType.REPEATED_FAILURE

    def evaluate(self, event_payload: dict[str, Any]) -> AlertCandidate | None:
        count = event_payload.get("consecutive_failure_count", 0)
        if count >= 3 or event_payload.get("repeated_failure", False):
            ds_id = event_payload.get("dataset_id")
            parsed_id = uuid.UUID(str(ds_id)) if ds_id else None
            target = event_payload.get("target_name", "pipeline")
            return AlertCandidate(
                alert_type=self.alert_type,
                severity=AlertSeverity.CRITICAL,
                title=f"Repeated Consecutive Failure ({count}x)",
                description=f"Target '{target}' failed {count} consecutive times without recovery.",
                dataset_id=parsed_id,
                target_entity_id=f"repeated:{ds_id}:{target}",
                metadata=event_payload,
            )
        return None
