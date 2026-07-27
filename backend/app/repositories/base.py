"""
Sentinel AI — Generic CRUD Repository

Provides a type-safe, reusable base for all data access operations.
Concrete repositories inherit from BaseRepository and add
domain-specific query methods.
"""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic async CRUD repository.

    Provides get, list, create, update, and delete operations
    that work with any SQLAlchemy model inheriting from Base.
    """

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelType | None:
        """Fetch a single entity by its primary key."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == entity_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        filters: list[Any] | None = None,
        order_by: Any | None = None,
    ) -> list[ModelType]:
        """Fetch a paginated list of entities with optional filters."""
        query = select(self._model)
        if filters:
            for condition in filters:
                query = query.where(condition)
        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self._model.created_at.desc())  # type: ignore[attr-defined]
        query = query.offset(offset).limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count(self, *, filters: list[Any] | None = None) -> int:
        """Count entities matching the given filters."""
        query: Select[tuple[int]] = select(func.count()).select_from(self._model)
        if filters:
            for condition in filters:
                query = query.where(condition)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def create(self, entity: ModelType) -> ModelType:
        """Persist a new entity and return it with generated fields populated."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: ModelType, update_data: dict[str, Any]) -> ModelType:
        """Apply partial updates to an existing entity."""
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Hard-delete an entity from the database."""
        await self._session.delete(entity)
        await self._session.flush()
