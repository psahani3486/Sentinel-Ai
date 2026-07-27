"""
Sentinel AI — User Management Service

Admin-level user operations: list, get, update, soft-delete.
Enforces business rules like preventing self-demotion
and protecting the last admin account.
"""

import logging
import math
import uuid
from typing import Any

from app.core.exceptions import (
    AuthorizationException,
    DuplicateEntityException,
    EntityNotFoundException,
    ValidationException,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """User management business logic (admin operations)."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """
        Fetch a user by ID.

        Raises:
            EntityNotFoundException: If user does not exist.
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundException("User", user_id)
        return user

    async def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        role: UserRole | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[UserResponse]:
        """
        List users with pagination and filters.

        Returns:
            PaginatedResponse containing serialized user records.
        """
        offset = (page - 1) * page_size

        users, total = await self._user_repo.get_users_paginated(
            offset=offset,
            limit=page_size,
            role=role,
            is_active=is_active,
            search=search,
        )

        return PaginatedResponse[UserResponse](
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max(1, math.ceil(total / page_size)),
        )

    async def update_user(
        self,
        user_id: uuid.UUID,
        update_data: dict[str, Any],
        current_user: User,
    ) -> User:
        """
        Update a user's profile (admin operation).

        Business rules:
        - Admins cannot demote themselves.
        - Email changes must not conflict with existing accounts.

        Raises:
            EntityNotFoundException: If user does not exist.
            AuthorizationException: If admin tries to demote self.
            DuplicateEntityException: If new email conflicts.
        """
        user = await self.get_user_by_id(user_id)

        # Prevent admin self-demotion
        if user.id == current_user.id and "role" in update_data:
            if update_data["role"] != current_user.role:
                raise AuthorizationException("Cannot change your own role")

        # Check email uniqueness if changing email
        if "email" in update_data and update_data["email"] != user.email:
            if await self._user_repo.email_exists(update_data["email"]):
                raise DuplicateEntityException("User", "email", update_data["email"])

        updated_user = await self._user_repo.update(user, update_data)
        logger.info(
            "User %s updated by admin %s: %s",
            user.email,
            current_user.email,
            list(update_data.keys()),
        )
        return updated_user

    async def deactivate_user(
        self,
        user_id: uuid.UUID,
        current_user: User,
    ) -> User:
        """
        Soft-delete a user by setting is_active to False.

        Business rules:
        - Cannot deactivate yourself.
        - Cannot deactivate the last active admin.

        Raises:
            EntityNotFoundException: If user does not exist.
            ValidationException: If this is the last admin.
            AuthorizationException: If trying to deactivate self.
        """
        user = await self.get_user_by_id(user_id)

        if user.id == current_user.id:
            raise AuthorizationException("Cannot deactivate your own account")

        # Protect last admin
        if user.role == UserRole.ADMIN:
            admins, admin_count = await self._user_repo.get_users_paginated(
                role=UserRole.ADMIN,
                is_active=True,
                limit=2,
            )
            if admin_count <= 1:
                raise ValidationException("Cannot deactivate the last active admin")

        deactivated = await self._user_repo.update(user, {"is_active": False})
        logger.info("User %s deactivated by admin %s", user.email, current_user.email)
        return deactivated
