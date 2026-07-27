"""
Sentinel AI — User Repository

Extends the generic CRUD repository with user-specific queries:
email lookup, role filtering, and search.
"""

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access layer for User entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address (case-insensitive)."""
        result = await self._session.execute(
            select(User).where(User.email.ilike(email))
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        user = await self.get_by_email(email)
        return user is not None

    async def get_active_users(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        """
        Fetch paginated active users with optional role filter and search.

        Returns:
            Tuple of (users_list, total_count).
        """
        filters: list[Any] = [User.is_active.is_(True)]

        if role is not None:
            filters.append(User.role == role)

        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term),
                )
            )

        users = await self.get_all(offset=offset, limit=limit, filters=filters)
        total = await self.count(filters=filters)

        return users, total

    async def get_users_paginated(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        """
        Fetch paginated users with comprehensive filters (admin view).

        Returns:
            Tuple of (users_list, total_count).
        """
        filters: list[Any] = []

        if role is not None:
            filters.append(User.role == role)

        if is_active is not None:
            filters.append(User.is_active.is_(is_active))

        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term),
                )
            )

        users = await self.get_all(offset=offset, limit=limit, filters=filters)
        total = await self.count(filters=filters)

        return users, total
