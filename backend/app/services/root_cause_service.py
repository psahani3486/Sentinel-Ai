"""
Sentinel AI — Root Cause Service

Service layer managing telemetry gathering, hybrid AI engine execution, and persistence of RCA reports.
"""

import logging
import uuid
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base_analyzer import AnalysisContext
from app.ai.engine import RootCauseEngine
from app.ai.reporter import AnalysisReporter
from app.models.ai import AnalysisEvidence, RootCauseAnalysis
from app.models.enums import AnalysisStatus, AnalysisType
from app.models.validation import ValidationResult
from app.repositories.ai_repository import AnalysisEvidenceRepository, RootCauseAnalysisRepository

logger = logging.getLogger(__name__)


class RootCauseService:
    """Coordinates telemetry gathering, hybrid RCA engine execution, and report persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        analysis_repo: RootCauseAnalysisRepository | None = None,
        evidence_repo: AnalysisEvidenceRepository | None = None,
        engine: RootCauseEngine | None = None,
        reporter: AnalysisReporter | None = None,
    ) -> None:
        self._session = db_session
        self._analysis_repo = analysis_repo or RootCauseAnalysisRepository(db_session)
        self._evidence_repo = evidence_repo or AnalysisEvidenceRepository(db_session)
        self._engine = engine or RootCauseEngine()
        self._reporter = reporter or AnalysisReporter()

    def _sanitize_dict(self, d: dict[str, Any]) -> dict[str, Any]:
        """Convert non-JSON serializable objects (such as UUIDs) into strings for JSON storage."""
        sanitized = {}
        for k, v in d.items():
            if isinstance(v, uuid.UUID):
                sanitized[k] = str(v)
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    async def run_root_cause_analysis(
        self,
        analysis_type: AnalysisType,
        target_entity_type: str,
        target_entity_id: str,
        dataset_id: uuid.UUID | None = None,
    ) -> RootCauseAnalysis:
        """Gather context, execute hybrid RCA engine, and persist report and evidence."""
        validation_results_data: list[dict[str, Any]] = []

        # Gather validation telemetry if target is validation run
        if target_entity_type == "validation_run":
            try:
                run_uuid = uuid.UUID(target_entity_id)
                stmt = select(ValidationResult).where(ValidationResult.validation_run_id == run_uuid)
                res = await self._session.execute(stmt)
                vr_list = res.scalars().all()
                for vr in vr_list:
                    validation_results_data.append({
                        "rule_type": vr.rule_type.value if hasattr(vr.rule_type, "value") else str(vr.rule_type),
                        "status": vr.status.value if hasattr(vr.status, "value") else str(vr.status),
                        "column_name": vr.affected_columns[0] if vr.affected_columns else None,
                        "message": vr.message,
                    })
            except Exception as err:
                logger.warning("Could not fetch validation results for RCA: %s", err)

        context = AnalysisContext(
            analysis_type=analysis_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            dataset_id=dataset_id,
            validation_results=validation_results_data,
        )

        # Execute Engine
        report = self._engine.run_root_cause_analysis(context)

        # Persist Analysis entity
        analysis_entity = RootCauseAnalysis(
            analysis_type=analysis_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            dataset_id=dataset_id,
            summary=report.summary,
            probable_root_cause=report.probable_root_cause,
            confidence_score=report.confidence_score,
            severity=report.severity,
            affected_components={"components": report.affected_components},
            recommended_actions={"actions": report.recommended_actions},
            status=AnalysisStatus.COMPLETED,
            execution_time_ms=report.execution_time_ms,
            llm_provider_name=report.llm_provider_name,
        )
        analysis_entity = await self._analysis_repo.create(analysis_entity)

        # Persist Evidences
        for ev in report.evidences:
            clean_payload = self._sanitize_dict(ev.evidence_payload)
            evidence_entity = AnalysisEvidence(
                analysis_id=analysis_entity.id,
                evidence_type=ev.evidence_type,
                title=ev.title,
                description=ev.description,
                evidence_payload=clean_payload,
                weight=ev.weight,
            )
            await self._evidence_repo.create(evidence_entity)

        logger.info("Executed AI RCA Analysis '%s' -> Type: %s, Confidence: %.1f%%",
                    analysis_entity.id, analysis_type.value, report.confidence_score)

        return await self._analysis_repo.get_by_id_with_evidences(analysis_entity.id) or analysis_entity

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[RootCauseAnalysis]:
        """Fetch paginated RCA report history."""
        return await self._analysis_repo.get_history(skip=skip, limit=limit)

    async def get_by_id(self, analysis_id: uuid.UUID) -> RootCauseAnalysis | None:
        """Fetch RCA report by ID with evidences."""
        return await self._analysis_repo.get_by_id_with_evidences(analysis_id)
