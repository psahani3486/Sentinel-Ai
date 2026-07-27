"""
Sentinel AI — Validation Service

Service layer managing data validation runs, score computations, and persistence
of ValidationRun and ValidationResult database entities.
"""

import logging
import uuid
from typing import Any

from app.models.enums import ConnectorType, RuleType, RunStatus, ValidationSeverity, ValidationStatus
from app.models.validation import ValidationResult, ValidationRun
from app.repositories.dataset_repository import DatasetVersionRepository
from app.repositories.validation_repository import (
    ValidationResultRepository,
    ValidationRunRepository,
)
from app.services.connector_service import ConnectorService
from app.validation_engine.base_rule import BaseValidationRule
from app.validation_engine.engine import ValidationEngine

logger = logging.getLogger(__name__)


class ValidationService:
    """Service layer coordinating validation engine execution and database persistence."""

    def __init__(
        self,
        connector_service: ConnectorService | None = None,
        validation_engine: ValidationEngine | None = None,
        run_repository: ValidationRunRepository | None = None,
        result_repository: ValidationResultRepository | None = None,
        version_repository: DatasetVersionRepository | None = None,
    ) -> None:
        self._connector_service = connector_service or ConnectorService()
        self._validation_engine = validation_engine or ValidationEngine()
        self._run_repo = run_repository
        self._result_repo = result_repository
        self._version_repo = version_repository

    def run_validation(
        self,
        connector_type: ConnectorType | str,
        config: dict[str, Any],
        rules: list[BaseValidationRule | dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Execute validation suite against target connector data source.

        Args:
            connector_type: Connector type enum or identifier string.
            config: Connector configuration dictionary.
            rules: Optional list of rule objects/configs.
            history: Optional past validation reports.

        Returns:
            Dict containing full validation report.
        """
        connector = self._connector_service.create_connector(connector_type, config)
        try:
            connector.connect()
            schema_info = connector.fetch_schema()
            df = connector.read()

            report = self._validation_engine.run_validations(
                df, rules=rules, schema_info=schema_info, history=history
            )
            return report
        finally:
            connector.disconnect()

    async def run_and_persist(
        self,
        dataset_version_id: uuid.UUID,
        connector_type: ConnectorType | str,
        config: dict[str, Any],
        rules: list[BaseValidationRule | dict[str, Any]] | None = None,
    ) -> ValidationRun:
        """
        Execute validation engine and persist ValidationRun & ValidationResult records into database.

        Raises:
            ValueError: If repositories were not injected into ValidationService.
        """
        if not self._run_repo or not self._result_repo:
            raise ValueError(
                "ValidationService requires ValidationRunRepository and ValidationResultRepository for persistence"
            )

        dataset_id = dataset_version_id
        if self._version_repo:
            ver = await self._version_repo.get_by_id(dataset_version_id)
            if ver:
                dataset_id = ver.dataset_id

        # 1. Create initial Pending ValidationRun
        run = ValidationRun(
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            status=RunStatus.RUNNING,
            overall_score=0.0,
        )
        run = await self._run_repo.create(run)

        try:
            # 2. Execute validation suite
            report = self.run_validation(
                connector_type, config, rules=rules, history=None
            )

            summary = report.get("summary", {})
            cat_scores = report.get("category_scores", {})
            overall_score = summary.get("overall_score", 100.0)
            failed_count = summary.get("failed_count", 0)

            run_status = RunStatus.COMPLETED if failed_count == 0 else RunStatus.FAILED

            # 3. Update ValidationRun entity
            updated_run = await self._run_repo.update(
                run,
                {
                    "status": run_status,
                    "overall_score": overall_score,
                    "completeness_score": cat_scores.get("completeness", 100.0),
                    "consistency_score": cat_scores.get("consistency", 100.0),
                    "accuracy_score": cat_scores.get("accuracy", 100.0),
                    "freshness_score": cat_scores.get("freshness", 100.0),
                    "execution_time_ms": summary.get("total_execution_time_ms", 0.0),
                },
            )

            # 4. Persist individual ValidationResult entities
            for r in report.get("failed_rules", []) + report.get("passed_rules", []) + report.get("warnings", []):
                rule_type_val = RuleType(r["rule_type"]) if isinstance(r["rule_type"], str) else r["rule_type"]
                status_val = ValidationStatus(r["status"]) if isinstance(r["status"], str) else r["status"]
                sev_val = ValidationSeverity(r["severity"]) if isinstance(r["severity"], str) else r["severity"]

                val_res = ValidationResult(
                    validation_run_id=updated_run.id,
                    rule_type=rule_type_val,
                    status=status_val,
                    severity=sev_val,
                    message=r["message"],
                    affected_columns=r.get("affected_columns", []),
                    affected_rows_count=r.get("affected_rows_count", 0),
                    execution_time_ms=r.get("execution_time_ms", 0.0),
                    score_impact=r.get("score_impact", 0.0),
                    details=r.get("details", {}),
                )
                await self._result_repo.create(val_res)

            logger.info("Persisted ValidationRun '%s' -> Score: %s", updated_run.id, overall_score)
            return updated_run

        except Exception as e:
            logger.error("ValidationRun '%s' failed: %s", run.id, str(e), exc_info=True)
            await self._run_repo.update(
                run,
                {
                    "status": RunStatus.FAILED,
                },
            )
            raise
