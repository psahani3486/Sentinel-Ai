"""
Sentinel AI — AI Repositories

Repository layer for persisting, querying, and loading RootCauseAnalysis and AnalysisEvidence entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.ai import AnalysisEvidence, RootCauseAnalysis
from app.repositories.base import BaseRepository


class RootCauseAnalysisRepository(BaseRepository[RootCauseAnalysis]):
    """Repository for managing RootCauseAnalysis entities."""

    def __init__(self, session) -> None:
        super().__init__(RootCauseAnalysis, session)

    async def get_by_id_with_evidences(self, analysis_id: uuid.UUID) -> RootCauseAnalysis | None:
        """Fetch RCA report by ID including relationship evidences."""
        stmt = (
            select(RootCauseAnalysis)
            .where(RootCauseAnalysis.id == analysis_id)
            .options(
                selectinload(RootCauseAnalysis.evidences),
                selectinload(RootCauseAnalysis.dataset),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[RootCauseAnalysis]:
        """Fetch paginated RCA history ordered by created_at desc."""
        stmt = (
            select(RootCauseAnalysis)
            .options(selectinload(RootCauseAnalysis.evidences))
            .order_by(RootCauseAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class AnalysisEvidenceRepository(BaseRepository[AnalysisEvidence]):
    """Repository for managing AnalysisEvidence entities."""

    def __init__(self, session) -> None:
        super().__init__(AnalysisEvidence, session)
