"""
Sentinel AI — Recommendation Repositories

Repository layer for persisting, querying, and sorting Recommendation and RecommendationEvidence entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.recommendation import Recommendation, RecommendationEvidence
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    """Repository for managing Recommendation entities and prioritized queries."""

    def __init__(self, session) -> None:
        super().__init__(Recommendation, session)

    async def get_by_id_with_evidences(self, rec_id: uuid.UUID) -> Recommendation | None:
        """Fetch Recommendation by ID including relationship evidences and RCA link."""
        stmt = (
            select(Recommendation)
            .where(Recommendation.id == rec_id)
            .options(
                selectinload(Recommendation.evidences),
                selectinload(Recommendation.rca),
                selectinload(Recommendation.dataset),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[Recommendation]:
        """Fetch paginated recommendations ordered by priority_score desc."""
        stmt = (
            select(Recommendation)
            .options(selectinload(Recommendation.evidences))
            .order_by(Recommendation.priority_score.desc(), Recommendation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class RecommendationEvidenceRepository(BaseRepository[RecommendationEvidence]):
    """Repository for managing RecommendationEvidence entities."""

    def __init__(self, session) -> None:
        super().__init__(RecommendationEvidence, session)
