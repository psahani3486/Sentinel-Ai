"""
Sentinel AI — Database Enumerations

Defines domain-specific string enums for datasets, connectors, validations, rules, background jobs, data drift, alert notifications, AI root cause analysis, remediation recommendations, predictive forecasting, incident workspace, workflow orchestration, plugin extension SDK, enterprise data catalog, platform telemetry observability, and enterprise policy engine governance.
"""

import enum


class DatasetType(str, enum.Enum):
    """Classification of data assets."""

    TABULAR = "tabular"
    TIME_SERIES = "time_series"
    SENSOR_STREAM = "sensor_stream"
    UNSTRUCTURED = "unstructured"


class ConnectorType(str, enum.Enum):
    """Supported data ingestion connectors."""

    CSV = "csv"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    INDUSTRIAL_SENSOR = "industrial_sensor"
    KAFKA = "kafka"
    S3 = "s3"


class ValidationSeverity(str, enum.Enum):
    """Impact level of a validation rule failure."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationStatus(str, enum.Enum):
    """Status of an individual validation rule evaluation."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class RunStatus(str, enum.Enum):
    """Status of a validation execution suite run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RuleType(str, enum.Enum):
    """Comprehensive list of supported data validation rule types."""

    MISSING_VALUES = "missing_values"
    DUPLICATE_ROWS = "duplicate_rows"
    INVALID_TIMESTAMPS = "invalid_timestamps"
    INVALID_NUMERIC_VALUES = "invalid_numeric_values"
    NEGATIVE_SENSOR_VALUES = "negative_sensor_values"
    OUTLIERS = "outliers"
    INVALID_SENSOR_RANGE = "invalid_sensor_range"
    CONSTANT_COLUMNS = "constant_columns"
    HIGH_CARDINALITY = "high_cardinality"
    LOW_CARDINALITY = "low_cardinality"
    NULL_COLUMNS = "null_columns"
    DUPLICATE_COLUMNS = "duplicate_columns"
    WRONG_DATA_TYPES = "wrong_data_types"
    SCHEMA_CHANGES = "schema_changes"
    FRESHNESS_VALIDATION = "freshness_validation"
    PRIMARY_KEY_VALIDATION = "primary_key_validation"
    UNIQUE_CONSTRAINT_VALIDATION = "unique_constraint_validation"
    COLUMN_STATISTICS = "column_statistics"
    DATA_COMPLETENESS = "data_completeness"
    DATA_CONSISTENCY = "data_consistency"
    DATA_ACCURACY = "data_accuracy"
    BUSINESS_RULE = "business_rule"


class JobStatus(str, enum.Enum):
    """Execution state of a background job."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Classification of background jobs."""

    DATASET_UPLOAD = "dataset_upload"
    DATA_PROFILING = "data_profiling"
    DATA_VALIDATION = "data_validation"


class JobPriority(str, enum.Enum):
    """Priority level for background job scheduling."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DriftStatus(str, enum.Enum):
    """Overall dataset data drift status."""

    NO_DRIFT = "no_drift"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DriftSeverity(str, enum.Enum):
    """Impact level of feature data drift."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DetectorType(str, enum.Enum):
    """Statistical algorithms for detecting feature distribution drift."""

    PSI = "psi"
    JENSEN_SHANNON = "jensen_shannon"
    KL_DIVERGENCE = "kl_divergence"
    WASSERSTEIN = "wasserstein"
    MEAN_DRIFT = "mean_drift"
    STD_DRIFT = "std_drift"
    MISSING_VALUE_DRIFT = "missing_value_drift"
    CARDINALITY_DRIFT = "cardinality_drift"
    CATEGORY_DISTRIBUTION_DRIFT = "category_distribution_drift"
    NUMERIC_DISTRIBUTION_DRIFT = "numeric_distribution_drift"


class AlertStatus(str, enum.Enum):
    """Lifecycle status of a platform incident alert."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertSeverity(str, enum.Enum):
    """Impact severity of a platform incident alert."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, enum.Enum):
    """Categorization of automated platform alerting rules."""

    QUALITY_SCORE_DROP = "quality_score_drop"
    VALIDATION_FAILURE = "validation_failure"
    CRITICAL_VALIDATION_RULE = "critical_validation_rule"
    SCHEMA_CHANGE = "schema_change"
    DATA_DRIFT = "data_drift"
    PIPELINE_FAILURE = "pipeline_failure"
    PIPELINE_TIMEOUT = "pipeline_timeout"
    JOB_FAILURE = "job_failure"
    DATASET_FRESHNESS = "dataset_freshness"
    REPEATED_FAILURE = "repeated_failure"


class AnalysisType(str, enum.Enum):
    """Categorization of AI Root Cause Analysis tasks."""

    VALIDATION_FAILURE = "validation_failure"
    DATA_DRIFT = "data_drift"
    SCHEMA_CHANGE = "schema_change"
    ALERT_CORRELATION = "alert_correlation"
    PIPELINE_FAILURE = "pipeline_failure"
    JOB_FAILURE = "job_failure"
    QUALITY_DEGRADATION = "quality_degradation"


class AnalysisStatus(str, enum.Enum):
    """Execution status of an AI Root Cause Analysis task."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class RecommendationPriority(str, enum.Enum):
    """Ranked priority score tier for remediation actions."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RecommendationCategory(str, enum.Enum):
    """Domain classification of remediation recommendation strategies."""

    VALIDATION_FAILURE = "validation_failure"
    SCHEMA_CHANGE = "schema_change"
    DATA_DRIFT = "data_drift"
    PIPELINE_FAILURE = "pipeline_failure"
    CONNECTOR_FAILURE = "connector_failure"
    JOB_FAILURE = "job_failure"
    QUALITY_SCORE_DROP = "quality_score_drop"
    ALERT_CORRELATION = "alert_correlation"
    MISSING_VALUES = "missing_values"
    OUTLIER_DETECTION = "outlier_detection"


class ForecastType(str, enum.Enum):
    """Categorization of predictive observability and risk forecasting tasks."""

    QUALITY_SCORE_TREND = "quality_score_trend"
    DATA_DRIFT_TREND = "data_drift_trend"
    VALIDATION_FAILURE_PROBABILITY = "validation_failure_probability"
    PIPELINE_FAILURE_PROBABILITY = "pipeline_failure_probability"
    JOB_FAILURE_PROBABILITY = "job_failure_probability"
    DATASET_FRESHNESS_FORECAST = "dataset_freshness_forecast"
    ALERT_VOLUME_FORECAST = "alert_volume_forecast"
    CONNECTOR_RELIABILITY_FORECAST = "connector_reliability_forecast"


class TrendDirection(str, enum.Enum):
    """Directional trend trajectory of a forecasted metric."""

    UPWARD = "upward"
    DOWNWARD = "downward"
    STABLE = "stable"


class RiskLevel(str, enum.Enum):
    """Predicted operational risk level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentStatus(str, enum.Enum):
    """Lifecycle status of a platform incident workspace."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSeverity(str, enum.Enum):
    """Impact severity of a correlated platform incident."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentEventType(str, enum.Enum):
    """Classification of timeline events inside an incident workspace."""

    VALIDATION_FAILED = "validation_failed"
    DRIFT_DETECTED = "drift_detected"
    SCHEMA_CHANGED = "schema_changed"
    ALERT_TRIGGERED = "alert_triggered"
    RCA_COMPLETED = "rca_completed"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    FORECAST_ALERT = "forecast_alert"
    JOB_FAILED = "job_failed"


class WorkflowState(str, enum.Enum):
    """State machine lifecycle states of a workflow execution run."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class WorkflowStepState(str, enum.Enum):
    """Execution state of an individual workflow step inside a DAG."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowType(str, enum.Enum):
    """Categorization of built-in Sentinel AI orchestration workflows."""

    DATASET_INGESTION = "dataset_ingestion"
    VALIDATION = "validation"
    PROFILING = "profiling"
    DRIFT_DETECTION = "drift_detection"
    ALERT = "alert"
    INCIDENT = "incident"
    ROOT_CAUSE = "root_cause"
    RECOMMENDATION = "recommendation"
    FORECAST = "forecast"
    END_TO_END_INVESTIGATION = "end_to_end_investigation"


class PluginStatus(str, enum.Enum):
    """Lifecycle state of a local plugin extension."""

    DISCOVERED = "discovered"
    VALIDATED = "validated"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UNLOADED = "unloaded"


class PluginType(str, enum.Enum):
    """Categorization of local plugin extensions."""

    CONNECTOR = "connector"
    VALIDATION_RULE = "validation_rule"
    PROFILING = "profiling"
    DRIFT_DETECTOR = "drift_detector"
    ALERT_RULE = "alert_rule"
    ANALYZER = "analyzer"
    RECOMMENDATION = "recommendation"
    FORECAST = "forecast"
    WORKFLOW = "workflow"
    DASHBOARD_WIDGET = "dashboard_widget"


class AssetType(str, enum.Enum):
    """Categorization of data catalog assets."""

    DATASET = "dataset"
    TABLE = "table"
    COLUMN = "column"
    PIPELINE = "pipeline"
    MODEL = "model"
    DASHBOARD = "dashboard"


class DataSensitivity(str, enum.Enum):
    """Security classification tier for data assets."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"


class LifecycleStatus(str, enum.Enum):
    """Lifecycle governance status of a data asset."""

    PROPOSED = "proposed"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class MetricType(str, enum.Enum):
    """Classification of platform telemetry metrics."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    REQUEST_COUNT = "request_count"
    ERROR_COUNT = "error_count"
    WORKER_UTILIZATION = "worker_utilization"
    QUEUE_DEPTH = "queue_depth"
    DURATION = "duration"


class SpanStatus(str, enum.Enum):
    """Execution status of an APM distributed tracing span."""

    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class HealthStatus(str, enum.Enum):
    """Subsystem operational health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class PolicyCategory(str, enum.Enum):
    """Categorization of enterprise policy governance rules."""

    DATASET_GOVERNANCE = "dataset_governance"
    SCHEMA = "schema"
    VALIDATION = "validation"
    QUALITY_THRESHOLD = "quality_threshold"
    DRIFT_THRESHOLD = "drift_threshold"
    WORKFLOW = "workflow"
    PLUGIN = "plugin"
    CATALOG_GOVERNANCE = "catalog_governance"
    RETENTION = "retention"
    INCIDENT_ESCALATION = "incident_escalation"


class PolicyStatus(str, enum.Enum):
    """Result status of a policy evaluation check."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class PolicySeverity(str, enum.Enum):
    """Impact severity of a policy compliance evaluation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
