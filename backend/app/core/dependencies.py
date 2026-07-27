"""
Sentinel AI — Core Dependency Injection

FastAPI `Depends()` providers that wire together the
Repository → Service → Endpoint chain.

Every request gets:
1. A fresh DB session (from get_async_session)
2. Repository instances bound to that session
3. Service instances bound to those repositories
4. The authenticated user (for protected routes)
"""

import logging
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, AuthorizationException
from app.db.session import get_async_session
from app.models.user import User, UserRole
from app.repositories.token_repository import UserRefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService

get_db = get_async_session

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

logger = logging.getLogger(__name__)


# ── DB Session & Repository Dependencies ─────────────────────────────────────

async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    """Provide a UserRepository bound to the request DB session."""
    return UserRepository(session)


async def get_token_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRefreshTokenRepository:
    """Provide a UserRefreshTokenRepository bound to the request DB session."""
    return UserRefreshTokenRepository(session)


# ── Service Dependencies ─────────────────────────────────────────────────────

async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    token_repo: Annotated[UserRefreshTokenRepository, Depends(get_token_repository)],
) -> AuthService:
    """Provide an AuthService bound to session repositories."""
    return AuthService(user_repo, token_repo)


AuthSvc = Annotated[AuthService, Depends(get_auth_service)]


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Provide a UserService bound to the user repository."""
    return UserService(user_repo)


UserSvc = Annotated[UserService, Depends(get_user_service)]


# ── Authentication (Token -> User) ───────────────────────────────────────────

async def get_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: str | None = Header(None, alias="Authorization"),
) -> User:
    """
    Extract JWT Bearer token from Header and validate current user.

    Raises:
        AuthenticationException: If Authorization header missing, malformed, or token invalid.
    """
    if not authorization:
        raise AuthenticationException("Authorization header is missing")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationException("Authorization header must be 'Bearer <token>'")

    token = parts[1]
    return await auth_service.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]


# ── Authorization (Role Guards) ──────────────────────────────────────────────

class RoleGuard:
    """
    Dependency that enforces minimum role requirements.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleGuard(UserRole.ADMIN))])
    """

    def __init__(self, *allowed_roles: UserRole) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: CurrentUser) -> User:
        if current_user.role not in self.allowed_roles:
            raise AuthorizationException(
                required_role=", ".join(r.value for r in self.allowed_roles),
            )
        return current_user


# Convenience guards
require_admin = RoleGuard(UserRole.ADMIN)
require_engineer = RoleGuard(UserRole.ADMIN, UserRole.DATA_ENGINEER, UserRole.ML_ENGINEER)
require_any_role = RoleGuard(UserRole.ADMIN, UserRole.DATA_ENGINEER, UserRole.ML_ENGINEER, UserRole.VIEWER)
