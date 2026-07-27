"""
Sentinel AI — Built-in Workflow Strategies

Implements 10 built-in workflow strategy DAGs:
1. Dataset Ingestion Workflow
2. Validation Workflow
3. Profiling Workflow
4. Drift Detection Workflow
5. Alert Workflow
6. Incident Workflow
7. Root Cause Workflow
8. Recommendation Workflow
9. Forecast Workflow
10. End-to-End Investigation Workflow
"""

from app.models.enums import WorkflowType
from app.workflows.base_workflow import BaseWorkflow, WorkflowStepDefinition


# ── 1. Dataset Ingestion Workflow ─────────────────────────────────────────────
class DatasetIngestionWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.DATASET_INGESTION

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("connect_source", "ConnectorTypeCheck"),
            WorkflowStepDefinition("parse_schema", "SchemaExtractor", depends_on=["connect_source"]),
            WorkflowStepDefinition("store_dataset", "StoragePersister", depends_on=["parse_schema"]),
        ]


# ── 2. Validation Workflow ────────────────────────────────────────────────────
class ValidationWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.VALIDATION

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("load_rules", "RuleRegistryFetch"),
            WorkflowStepDefinition("evaluate_suite", "RuleExecutionEngine", depends_on=["load_rules"]),
            WorkflowStepDefinition("calculate_score", "QualityScoreCalculator", depends_on=["evaluate_suite"]),
        ]


# ── 3. Profiling Workflow ─────────────────────────────────────────────────────
class ProfilingWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.PROFILING

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("compute_stats", "ColumnStatisticsCalculator"),
            WorkflowStepDefinition("extract_metadata", "MetadataExtractor", depends_on=["compute_stats"]),
            WorkflowStepDefinition("generate_insights", "InsightEngine", depends_on=["extract_metadata"]),
        ]


# ── 4. Drift Detection Workflow ───────────────────────────────────────────────
class DriftDetectionWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.DRIFT_DETECTION

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("fetch_reference", "ReferenceDistributionFetch"),
            WorkflowStepDefinition("calculate_psi", "PSIDriftDetector", depends_on=["fetch_reference"]),
            WorkflowStepDefinition("evaluate_drift_risk", "DriftReporter", depends_on=["calculate_psi"]),
        ]


# ── 5. Alert Workflow ─────────────────────────────────────────────────────────
class AlertWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.ALERT

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("evaluate_alert_rules", "AlertRuleEvaluator"),
            WorkflowStepDefinition("deduplicate_alerts", "AlertDeduplicator", depends_on=["evaluate_alert_rules"]),
            WorkflowStepDefinition("notify_channels", "AlertDispatcher", depends_on=["deduplicate_alerts"]),
        ]


# ── 6. Incident Workflow ──────────────────────────────────────────────────────
class IncidentWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.INCIDENT

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("correlate_signals", "SignalCorrelator"),
            WorkflowStepDefinition("build_timeline", "TimelineBuilder", depends_on=["correlate_signals"]),
            WorkflowStepDefinition("create_workspace", "IncidentWorkspaceCreator", depends_on=["build_timeline"]),
        ]


# ── 7. Root Cause Workflow ────────────────────────────────────────────────────
class RootCauseWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.ROOT_CAUSE

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("gather_telemetry", "TelemetryCollector"),
            WorkflowStepDefinition("execute_analyzers", "AnalyzerExecutor", depends_on=["gather_telemetry"]),
            WorkflowStepDefinition("synthesize_llm", "LLMExplanationSynthesizer", depends_on=["execute_analyzers"]),
        ]


# ── 8. Recommendation Workflow ────────────────────────────────────────────────
class RecommendationWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.RECOMMENDATION

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("evaluate_strategies", "RecommendationStrategyEvaluator"),
            WorkflowStepDefinition("compute_priority_score", "PrioritizationRanker", depends_on=["evaluate_strategies"]),
            WorkflowStepDefinition("format_action_plan", "ActionPlanFormatter", depends_on=["compute_priority_score"]),
        ]


# ── 9. Forecast Workflow ──────────────────────────────────────────────────────
class ForecastWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.FORECAST

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("extract_time_series", "TimeSeriesExtractor"),
            WorkflowStepDefinition("fit_ols_model", "LinearRegressionModelFit", depends_on=["extract_time_series"]),
            WorkflowStepDefinition("calculate_confidence_bounds", "ConfidenceIntervalCalculator", depends_on=["fit_ols_model"]),
        ]


# ── 10. End-to-End Investigation Workflow ──────────────────────────────────────
class EndToEndInvestigationWorkflow(BaseWorkflow):
    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.END_TO_END_INVESTIGATION

    def get_step_definitions(self) -> list[WorkflowStepDefinition]:
        return [
            WorkflowStepDefinition("ingest", "DatasetIngest"),
            WorkflowStepDefinition("profile", "DatasetProfile", depends_on=["ingest"]),
            WorkflowStepDefinition("validate", "DatasetValidate", depends_on=["ingest"]),
            WorkflowStepDefinition("drift", "DriftDetect", depends_on=["profile"]),
            WorkflowStepDefinition("alerts", "AlertEvaluate", depends_on=["validate"]),
            WorkflowStepDefinition("rca", "RootCauseAnalyze", depends_on=["validate", "alerts"]),
            WorkflowStepDefinition("recommendation", "RecommendationGenerate", depends_on=["rca"]),
            WorkflowStepDefinition("incident", "IncidentCorrelate", depends_on=["rca", "recommendation"]),
            WorkflowStepDefinition("forecast", "RiskForecast", depends_on=["drift", "incident"]),
        ]
