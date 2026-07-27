"""
Sentinel AI — Dataset Repositories

Provides database access operations for Datasets, Versions, Schemas, Columns, and Profiles.
"""

import uuid
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.dataset import (
    Dataset,
    DatasetColumn,
    DatasetProfile,
    DatasetSchema,
    DatasetVersion,
)
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    """Repository for Dataset entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(Dataset, session)

    async def get_by_id_with_relations(self, dataset_id: uuid.UUID) -> Dataset | None:
        """Fetch a dataset by ID including its latest version and relationships."""
        result = await self._session.execute(
            select(Dataset)
            .options(selectinload(Dataset.versions))
            .where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(
        self,
        owner_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Dataset]:
        """Fetch datasets owned by a specific user."""
        result = await self._session.execute(
            select(Dataset)
            .where(Dataset.owner_id == owner_id, Dataset.is_active.is_(True))
            .order_by(Dataset.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_datasets_paginated(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: bool | None = True,
        connector_type: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Dataset], int]:
        """Fetch paginated datasets with optional search and filtering."""
        query = select(Dataset).options(selectinload(Dataset.versions))
        filters: list[Any] = []

        if is_active is not None:
            filters.append(Dataset.is_active == is_active)
        if connector_type:
            filters.append(Dataset.connector_type == connector_type)
        if search:
            filters.append(
                Dataset.name.ilike(f"%{search}%") | Dataset.description.ilike(f"%{search}%")
            )

        for cond in filters:
            query = query.where(cond)

        # Count total matching
        count_query = select(func.count()).select_from(Dataset)
        for cond in filters:
            count_query = count_query.where(cond)
        count_res = await self._session.execute(count_query)
        total = count_res.scalar_one()

        # Execute paginated query
        query = query.order_by(Dataset.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def exists_by_owner_and_name(self, owner_id: uuid.UUID, name: str) -> bool:
        """Check if a dataset with the given name already exists for an owner."""
        result = await self._session.execute(
            select(Dataset).where(
                Dataset.owner_id == owner_id,
                Dataset.name == name,
                Dataset.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None


class DatasetVersionRepository(BaseRepository[DatasetVersion]):
    """Repository for DatasetVersion entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(DatasetVersion, session)

    async def get_latest_version(self, dataset_id: uuid.UUID) -> DatasetVersion | None:
        """Fetch the most recent version of a dataset."""
        result = await self._session.execute(
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset_id)
            .order_by(DatasetVersion.version_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_dataset_and_version(
        self, dataset_id: uuid.UUID, version_number: int
    ) -> DatasetVersion | None:
        """Fetch a specific dataset version by number."""
        result = await self._session.execute(
            select(DatasetVersion).where(
                DatasetVersion.dataset_id == dataset_id,
                DatasetVersion.version_number == version_number,
            )
        )
        return result.scalar_one_or_none()


class DatasetSchemaRepository(BaseRepository[DatasetSchema]):
    """Repository for DatasetSchema entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(DatasetSchema, session)

    async def get_by_version_id(self, version_id: uuid.UUID) -> DatasetSchema | None:
        """Fetch a dataset schema with column details by version ID."""
        result = await self._session.execute(
            select(DatasetSchema)
            .options(selectinload(DatasetSchema.columns))
            .where(DatasetSchema.dataset_version_id == version_id)
        )
        return result.scalar_one_or_none()


class DatasetColumnRepository(BaseRepository[DatasetColumn]):
    """Repository for DatasetColumn entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(DatasetColumn, session)

    async def get_columns_by_schema_id(self, schema_id: uuid.UUID) -> list[DatasetColumn]:
        """Fetch ordered columns for a dataset schema."""
        result = await self._session.execute(
            select(DatasetColumn)
            .where(DatasetColumn.dataset_schema_id == schema_id)
            .order_by(DatasetColumn.position)
        )
        return list(result.scalars().all())


class DatasetProfileRepository(BaseRepository[DatasetProfile]):
    """Repository for DatasetProfile entities."""

    def __init__(self, session: Any) -> None:
        super().__init__(DatasetProfile, session)

    async def get_by_version_id(self, version_id: uuid.UUID) -> DatasetProfile | None:
        """Fetch profile details for a dataset version."""
        result = await self._session.execute(
            select(DatasetProfile).where(DatasetProfile.dataset_version_id == version_id)
        )
        return result.scalar_one_or_none()
