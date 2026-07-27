"""
Sentinel AI — Validation Repositories

Provides database access operations for Validation Rules, Validation Runs, and Validation Results.
"""

import uuid
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.enums import RuleType, RunStatus, ValidationStatus
from app.models.validation import ValidationResult, ValidationRule, ValidationRun
from app.repositories.base import BaseRepository


class ValidationRuleRepository(BaseRepository[ValidationRule]):
    """Repository for ValidationRule entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(ValidationRule, session)

    async def get_active_rules(self) -> list[ValidationRule]:
        """Fetch all enabled validation rules."""
        result = await self._session.execute(
            select(ValidationRule)
            .where(ValidationRule.is_active.is_(True))
            .order_by(ValidationRule.name)
        )
        return list(result.scalars().all())

    async def get_by_rule_type(self, rule_type: RuleType) -> list[ValidationRule]:
        """Fetch validation rules by rule type."""
        result = await self._session.execute(
            select(ValidationRule).where(
                ValidationRule.rule_type == rule_type,
                ValidationRule.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> ValidationRule | None:
        """Fetch rule by name."""
        result = await self._session.execute(
            select(ValidationRule).where(ValidationRule.name == name)
        )
        return result.scalar_one_or_none()


class ValidationRunRepository(BaseRepository[ValidationRun]):
    """Repository for ValidationRun entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(ValidationRun, session)

    async def get_run_with_results(self, run_id: uuid.UUID) -> ValidationRun | None:
        """Fetch a validation run along with all its detailed execution results."""
        result = await self._session.execute(
            select(ValidationRun)
            .options(selectinload(ValidationRun.results))
            .where(ValidationRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_runs_by_dataset(
        self,
        dataset_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ValidationRun], int]:
        """Fetch paginated validation runs for a dataset."""
        count_res = await self._session.execute(
            select(func.count())
            .select_from(ValidationRun)
            .where(ValidationRun.dataset_id == dataset_id)
        )
        total = count_res.scalar_one()

        result = await self._session.execute(
            select(ValidationRun)
            .where(ValidationRun.dataset_id == dataset_id)
            .order_by(ValidationRun.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_latest_run(self, dataset_id: uuid.UUID) -> ValidationRun | None:
        """Fetch the most recent validation run for a dataset."""
        result = await self._session.execute(
            select(ValidationRun)
            .options(selectinload(ValidationRun.results))
            .where(ValidationRun.dataset_id == dataset_id, ValidationRun.status == RunStatus.COMPLETED)
            .order_by(ValidationRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ValidationResultRepository(BaseRepository[ValidationResult]):
    """Repository for ValidationResult entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(ValidationResult, session)

    async def get_results_by_run_id(self, run_id: uuid.UUID) -> list[ValidationResult]:
        """Fetch all execution results for a specific validation run."""
        result = await self._session.execute(
            select(ValidationResult)
            .where(ValidationResult.validation_run_id == run_id)
            .order_by(ValidationResult.severity.desc())
        )
        return list(result.scalars().all())

    async def get_failed_results_by_run_id(self, run_id: uuid.UUID) -> list[ValidationResult]:
        """Fetch only failed/warning results for a validation run."""
        result = await self._session.execute(
            select(ValidationResult)
            .where(
                ValidationResult.validation_run_id == run_id,
                ValidationResult.status.in_([ValidationStatus.FAILED, ValidationStatus.WARNING, ValidationStatus.ERROR]),
            )
            .order_by(ValidationResult.severity.desc())
        )
        return list(result.scalars().all())
