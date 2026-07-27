"""
Sentinel AI — Recommendation Service

Service layer managing telemetry context gathering, recommendation generation,
priority score ranking, and report persistence.
"""

import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecommendationCategory
from app.models.recommendation import Recommendation, RecommendationEvidence
from app.recommendation_engine.base_strategy import RecommendationContext
from app.recommendation_engine.engine import RecommendationEngine
from app.recommendation_engine.reporter import RecommendationReporter
from app.repositories.ai_repository import RootCauseAnalysisRepository
from app.repositories.recommendation_repository import (
    RecommendationEvidenceRepository,
    RecommendationRepository,
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """Coordinates remediation recommendation generation, weighted scoring, and report persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        rec_repo: RecommendationRepository | None = None,
        evidence_repo: RecommendationEvidenceRepository | None = None,
        rca_repo: RootCauseAnalysisRepository | None = None,
        engine: RecommendationEngine | None = None,
        reporter: RecommendationReporter | None = None,
    ) -> None:
        self._session = db_session
        self._rec_repo = rec_repo or RecommendationRepository(db_session)
        self._evidence_repo = evidence_repo or RecommendationEvidenceRepository(db_session)
        self._rca_repo = rca_repo or RootCauseAnalysisRepository(db_session)
        self._engine = engine or RecommendationEngine()
        self._reporter = reporter or RecommendationReporter()

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

    async def generate_recommendations(
        self,
        category: RecommendationCategory,
        rca_id: uuid.UUID | None = None,
        dataset_id: uuid.UUID | None = None,
    ) -> Recommendation:
        """Gather context, execute recommendation engine, and persist recommendation and evidence."""
        rca_summary = None
        rca_root_cause = None

        if rca_id:
            try:
                rca = await self._rca_repo.get_by_id(rca_id)
                if rca:
                    rca_summary = rca.summary
                    rca_root_cause = rca.probable_root_cause
                    if not dataset_id:
                        dataset_id = rca.dataset_id
            except Exception as err:
                logger.warning("Could not fetch RCA report '%s' for recommendation context: %s", rca_id, err)

        context = RecommendationContext(
            category=category,
            rca_id=rca_id,
            dataset_id=dataset_id,
            rca_summary=rca_summary,
            rca_probable_root_cause=rca_root_cause,
        )

        # Execute Engine
        res = self._engine.generate_recommendation(context)

        # Persist Recommendation entity
        rec_entity = Recommendation(
            rca_id=rca_id,
            dataset_id=dataset_id,
            category=category,
            priority=res.priority,
            title=res.title,
            description=res.description,
            estimated_impact=res.estimated_impact,
            estimated_effort=res.estimated_effort,
            confidence_score=res.confidence_score,
            priority_score=res.priority_score,
            suggested_next_steps={"steps": res.suggested_next_steps},
            status="active",
            execution_time_ms=res.execution_time_ms,
        )
        rec_entity = await self._rec_repo.create(rec_entity)

        # Persist Evidences
        for ev in res.evidences:
            clean_payload = self._sanitize_dict(ev.evidence_payload)
            evidence_entity = RecommendationEvidence(
                recommendation_id=rec_entity.id,
                title=ev.title,
                description=ev.description,
                evidence_payload=clean_payload,
                weight=ev.weight,
            )
            await self._evidence_repo.create(evidence_entity)

        logger.info("Generated Recommendation '%s' -> Category: %s, Priority Score: %.1f",
                    rec_entity.id, category.value, res.priority_score)

        return await self._rec_repo.get_by_id_with_evidences(rec_entity.id) or rec_entity

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[Recommendation]:
        """Fetch paginated recommendation history ordered by priority_score desc."""
        return await self._rec_repo.get_history(skip=skip, limit=limit)

    async def get_by_id(self, rec_id: uuid.UUID) -> Recommendation | None:
        """Fetch recommendation by ID with evidences."""
        return await self._rec_repo.get_by_id_with_evidences(rec_id)
