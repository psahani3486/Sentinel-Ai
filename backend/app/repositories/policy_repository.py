"""
Sentinel AI — Policy Repositories

Repository layer for persisting, querying, and updating PolicyDefinition and PolicyEvaluation entities.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.policy import PolicyDefinition, PolicyEvaluation
from app.repositories.base import BaseRepository


class PolicyDefinitionRepository(BaseRepository[PolicyDefinition]):
    """Repository for managing PolicyDefinition entities."""

    def __init__(self, session) -> None:
        super().__init__(PolicyDefinition, session)

    async def get_by_name(self, name: str) -> PolicyDefinition | None:
        """Fetch PolicyDefinition by policy_name."""
        stmt = select(PolicyDefinition).where(PolicyDefinition.policy_name == name)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all_active(self) -> Sequence[PolicyDefinition]:
        """Fetch active policy definitions ordered by category asc, policy_name asc."""
        stmt = (
            select(PolicyDefinition)
            .where(PolicyDefinition.is_active.is_(True))
            .order_by(PolicyDefinition.category.asc(), PolicyDefinition.policy_name.asc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class PolicyEvaluationRepository(BaseRepository[PolicyEvaluation]):
    """Repository for managing PolicyEvaluation entities."""

    def __init__(self, session) -> None:
        super().__init__(PolicyEvaluation, session)

    async def get_recent_evaluations(self, limit: int = 50) -> Sequence[PolicyEvaluation]:
        """Fetch recent policy evaluations ordered by evaluated_at desc with policy_definition eager-loaded."""
        stmt = (
            select(PolicyEvaluation)
            .options(selectinload(PolicyEvaluation.policy_definition))
            .order_by(PolicyEvaluation.evaluated_at.desc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()
