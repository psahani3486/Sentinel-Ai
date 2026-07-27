"""
Sentinel AI — Policy Service

Service layer managing enterprise policy evaluations, rule catalog querying, and persistence.
"""

import datetime
import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import PolicyDefinition, PolicyEvaluation
from app.policies.engine import PolicyEngine
from app.policies.reporter import PolicyReporter
from app.repositories.policy_repository import (
    PolicyDefinitionRepository,
    PolicyEvaluationRepository,
)

logger = logging.getLogger(__name__)


class PolicyService:
    """Coordinates policy suite execution, compliance reporting, and policy rule persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        def_repo: PolicyDefinitionRepository | None = None,
        eval_repo: PolicyEvaluationRepository | None = None,
        engine: PolicyEngine | None = None,
        reporter: PolicyReporter | None = None,
    ) -> None:
        self._session = db_session
        self._def_repo = def_repo or PolicyDefinitionRepository(db_session)
        self._eval_repo = eval_repo or PolicyEvaluationRepository(db_session)
        self._engine = engine or PolicyEngine()
        self._reporter = reporter or PolicyReporter()

    async def seed_initial_policies(self) -> Sequence[PolicyDefinition]:
        """Seed initial 10 enterprise policy rule definitions."""
        active = await self._def_repo.get_all_active()
        if not active:
            for p in self._engine._registry.get_all():
                p_entity = PolicyDefinition(
                    policy_name=p.policy_name,
                    category=p.category,
                    severity=p.severity,
                    description=f"Enterprise governance policy rule: {p.policy_name}",
                    rules_spec={"policy_id": p.policy_id},
                    is_active=True,
                )
                await self._def_repo.create(p_entity)

            logger.info("Seeded 10 default enterprise policy rule definitions.")

        return await self._def_repo.get_all_active()

    async def evaluate_policies(self, target: dict[str, Any] | None = None) -> list[PolicyEvaluation]:
        """Execute policy Specification suite and persist PolicyEvaluation records."""
        definitions = await self.seed_initial_policies()
        def_map = {d.policy_name: d for d in definitions}

        results = self._engine.evaluate_suite(target)
        evaluations = []
        now = datetime.datetime.now(datetime.timezone.utc)

        for r in results:
            p_def = def_map.get(r.policy_name)
            if p_def:
                e_entity = PolicyEvaluation(
                    policy_id=p_def.id,
                    status=r.status,
                    severity=r.severity,
                    evidence=r.evidence,
                    recommendation=r.recommendation,
                    evaluated_at=now,
                )
                e_entity = await self._eval_repo.create(e_entity)
                e_entity.policy_definition = p_def
                evaluations.append(e_entity)

        return evaluations

    async def get_policies(self) -> Sequence[PolicyDefinition]:
        """Fetch active policy definitions."""
        policies = await self._def_repo.get_all_active()
        if not policies:
            return await self.seed_initial_policies()
        return policies

    async def get_policy_detail(self, policy_id: uuid.UUID) -> PolicyDefinition | None:
        """Fetch detailed policy definition by UUID."""
        return await self._def_repo.get_by_id(policy_id)

    async def get_evaluations(self) -> Sequence[PolicyEvaluation]:
        """Fetch recent policy evaluation results."""
        evals = await self._eval_repo.get_recent_evaluations()
        if not evals:
            await self.evaluate_policies()
            return await self._eval_repo.get_recent_evaluations()
        return evals
