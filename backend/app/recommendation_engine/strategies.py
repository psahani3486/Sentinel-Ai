"""
Sentinel AI — Automated Remediation Recommendation Strategies

Implements 10 independent remediation recommendation strategies:
1. Validation Failure
2. Schema Change
3. Data Drift
4. Pipeline Failure
5. Connector Failure
6. Job Failure
7. Quality Score Drop
8. Alert Correlation
9. Missing Values
10. Outlier Detection
"""

from app.models.enums import RecommendationCategory, RecommendationPriority
from app.recommendation_engine.base_strategy import (
    BaseRecommendationStrategy,
    EvidenceItem,
    RawRecommendationCandidate,
    RecommendationContext,
)


# ── 1. Validation Failure Strategy ─────────────────────────────────────────────
class ValidationFailureRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.VALIDATION_FAILURE

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        cols = context.rca_affected_components or ["dataset"]
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.HIGH,
            title=f"Remediate Data Validation Failures on {cols}",
            description="Enforce strict pre-ingestion type casting and sanitize malformed string representations.",
            estimated_impact="HIGH",
            estimated_effort="LOW",
            confidence_score=92.0,
            suggested_next_steps=[
                "Filter or cast unparseable string values prior to SQL database insert.",
                "Update validation rule parameters to tolerate expected operational noise bounds.",
                "Trigger automated validation suite re-run.",
            ],
            evidences=[
                EvidenceItem(
                    title="Validation Suite Telemetry",
                    description=f"Target entity '{context.rca_id or 'run'}' failed validation contracts.",
                    weight=0.9,
                )
            ],
        )


# ── 2. Schema Change Strategy ──────────────────────────────────────────────────
class SchemaChangeRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.SCHEMA_CHANGE

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.HIGH,
            title="Synchronize Database ORM Schema with Upstream Evolution",
            description="Update target table definitions and execute Alembic database migration scripts.",
            estimated_impact="HIGH",
            estimated_effort="MEDIUM",
            confidence_score=95.0,
            suggested_next_steps=[
                "Run `alembic revision --autogenerate` to catch missing or altered columns.",
                "Deploy updated SQLAlchemy ORM model definitions.",
                "Notify downstream data warehouse consumers.",
            ],
            evidences=[
                EvidenceItem(
                    title="Schema Evolution Event",
                    description="Column structure mismatch detected between database table and ingest payload.",
                    weight=0.95,
                )
            ],
        )


# ── 3. Data Drift Strategy ─────────────────────────────────────────────────────
class DataDriftRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.DATA_DRIFT

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.MEDIUM,
            title="Re-Baseline Data Drift Reference Distributions",
            description="Re-calibrate baseline feature quantiles if distribution shift reflects valid operational evolution.",
            estimated_impact="MEDIUM",
            estimated_effort="LOW",
            confidence_score=88.0,
            suggested_next_steps=[
                "Inspect dual-histogram distribution overlay in Data Drift Observatory.",
                "Promote latest ingested dataset version to reference baseline.",
                "Adjust PSI alert sensitivity threshold if natural seasonal variation is present.",
            ],
            evidences=[
                EvidenceItem(
                    title="Population Stability Index Alert",
                    description="Feature quantiles shifted beyond PSI 0.10 threshold.",
                    weight=0.85,
                )
            ],
        )


# ── 4. Pipeline Failure Strategy ───────────────────────────────────────────────
class PipelineFailureRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.PIPELINE_FAILURE

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.CRITICAL,
            title="Restore Pipeline Database Connection & Timeout Limits",
            description="Verify database credentials, network connection strings, and socket timeout parameters.",
            estimated_impact="HIGH",
            estimated_effort="LOW",
            confidence_score=94.0,
            suggested_next_steps=[
                "Verify database connection string and password secrets in vault.",
                "Increase pipeline execution timeout limit from 5 to 15 minutes.",
                "Trigger manual pipeline retry execution.",
            ],
            evidences=[
                EvidenceItem(
                    title="Pipeline Execution Error Log",
                    description="Ingestion pipeline connection socket timed out during batch fetch.",
                    weight=0.9,
                )
            ],
        )


# ── 5. Connector Failure Strategy ──────────────────────────────────────────────
class ConnectorFailureRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.CONNECTOR_FAILURE

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.HIGH,
            title="Update Data Ingestion Connector Driver & Proxy Configuration",
            description="Re-authenticate ingestion connector and update network proxy certificates.",
            estimated_impact="HIGH",
            estimated_effort="MEDIUM",
            confidence_score=90.0,
            suggested_next_steps=[
                "Test connection credentials via `POST /connectors/{id}/test` endpoint.",
                "Update connector driver dependencies.",
                "Re-enable scheduled ingestion cron job.",
            ],
            evidences=[
                EvidenceItem(
                    title="Connector Disconnection Telemetry",
                    description="Ingestion connector driver failed connection handshake.",
                    weight=0.9,
                )
            ],
        )


# ── 6. Job Failure Strategy ────────────────────────────────────────────────────
class JobFailureRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.JOB_FAILURE

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.HIGH,
            title="Scale Worker Memory Allocation for Background Queues",
            description="Increase memory limits and concurrency bounds for worker processes processing large datasets.",
            estimated_impact="HIGH",
            estimated_effort="LOW",
            confidence_score=91.0,
            suggested_next_steps=[
                "Increase worker process RAM allocation to 4GB.",
                "Re-queue failed job ID via Job Service.",
                "Inspect worker error logs in Redis dashboard.",
            ],
            evidences=[
                EvidenceItem(
                    title="Worker Task Exception Log",
                    description="Worker task process crashed during profiling chunk execution.",
                    weight=0.9,
                )
            ],
        )


# ── 7. Quality Score Drop Strategy ─────────────────────────────────────────────
class QualityScoreDropRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.QUALITY_SCORE_DROP

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.CRITICAL,
            title="Enforce Quality SLA Gate before Analytical Ingestion",
            description="Block downstream analytical ingestion when overall quality score drops below target SLA (85%).",
            estimated_impact="HIGH",
            estimated_effort="LOW",
            confidence_score=96.0,
            suggested_next_steps=[
                "Enable hard quality gate on pipeline ingestion pipeline.",
                "Purge corrupted batch rows from staging table.",
                "Re-evaluate quality score following data repair.",
            ],
            evidences=[
                EvidenceItem(
                    title="Quality Score Drop Metric",
                    description="Dataset quality score dropped to 68.5% (SLA target: 85%).",
                    weight=0.95,
                )
            ],
        )


# ── 8. Alert Correlation Strategy ──────────────────────────────────────────────
class AlertCorrelationRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.ALERT_CORRELATION

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.HIGH,
            title="Acknowledge Correlated Incident Alerts & Suppress Noise",
            description="Group active correlated alerts in Alert Center and resolve root pipeline failure.",
            estimated_impact="MEDIUM",
            estimated_effort="LOW",
            confidence_score=87.0,
            suggested_next_steps=[
                "Acknowledge open incident notifications in Alert Center.",
                "Resolve root pipeline disconnect event.",
                "Verify alert noise suppression rules.",
            ],
            evidences=[
                EvidenceItem(
                    title="Correlated Alert Cluster",
                    description="Multiple alerts triggered simultaneously on target asset.",
                    weight=0.85,
                )
            ],
        )


# ── 9. Missing Values Strategy ─────────────────────────────────────────────────
class MissingValuesRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.MISSING_VALUES

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.MEDIUM,
            title="Apply Mean/Median Null Imputation & NOT NULL Constraints",
            description="Fill missing null values using statistical imputation or enforce SQL NOT NULL column constraints.",
            estimated_impact="MEDIUM",
            estimated_effort="LOW",
            confidence_score=93.0,
            suggested_next_steps=[
                "Apply median value imputation on numeric sensor columns.",
                "Add default values or NOT NULL constraint in SQL migration.",
            ],
            evidences=[
                EvidenceItem(
                    title="Null Column Rule Violation",
                    description="Column contains missing null values exceeding tolerance.",
                    weight=0.9,
                )
            ],
        )


# ── 10. Outlier Detection Strategy ─────────────────────────────────────────────
class OutlierDetectionRecommendationStrategy(BaseRecommendationStrategy):
    @property
    def category(self) -> RecommendationCategory:
        return RecommendationCategory.OUTLIER_DETECTION

    def generate(self, context: RecommendationContext) -> RawRecommendationCandidate:
        return RawRecommendationCandidate(
            category=self.category,
            priority=RecommendationPriority.LOW,
            title="Apply IQR Winsorization / Trimming to Outlier Sensor Columns",
            description="Clip extreme outlier values beyond 3 standard deviations to prevent model distortion.",
            estimated_impact="LOW",
            estimated_effort="LOW",
            confidence_score=89.0,
            suggested_next_steps=[
                "Apply IQR 1.5x winsorization on sensor column.",
                "Review outlier bounds in Data Profiling Inspector.",
            ],
            evidences=[
                EvidenceItem(
                    title="Outlier Detection Metric",
                    description="Values exceeded 3 sigma bounds in numerical feature.",
                    weight=0.85,
                )
            ],
        )
