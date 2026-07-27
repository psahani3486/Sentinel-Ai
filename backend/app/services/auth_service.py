"""
Sentinel AI — Authentication Service

Encapsulates all authentication business logic:
- User registration (with duplicate check)
- Login (credential validation + token issuance)
- Token refresh
- Current user retrieval

This service never touches HTTP concerns — it receives and returns
plain Python objects. The API layer handles serialization.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.core.exceptions import (
    AuthenticationException,
    DuplicateEntityException,
    EntityNotFoundException,
    TokenException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.models.token import UserRefreshToken
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import UserRefreshTokenRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and authorization business logic."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: UserRefreshTokenRepository,
    ) -> None:
        self._user_repo = user_repository
        self._token_repo = token_repository

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.VIEWER,
    ) -> User:
        """
        Register a new user account with specified RBAC role.
        """
        if await self._user_repo.email_exists(email):
            raise DuplicateEntityException("User", "email", email)

        user = User(
            email=email.lower().strip(),
            hashed_password=hash_password(password),
            full_name=full_name.strip(),
            role=role,
            is_active=True,
            is_superuser=(role == UserRole.ADMIN),
        )

        created_user = await self._user_repo.create(user)
        logger.info("New user registered: %s (role: %s)", created_user.email, created_user.role.value)
        return created_user

    async def login(self, email: str, password: str) -> tuple[User, str, str]:
        """
        Authenticate a user and issue tokens.

        Returns:
            Tuple of (user, access_token, refresh_token).

        Raises:
            AuthenticationException: If credentials are invalid or account is inactive.
        """
        user = await self._user_repo.get_by_email(email)

        if user is None:
            raise AuthenticationException("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        # Update last login timestamp
        await self._user_repo.update(user, {"last_login_at": datetime.now(timezone.utc)})

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value},
        )
        refresh_token, jti, expires_at = create_refresh_token(subject=str(user.id))

        # Store the token JTI in the database
        db_token = UserRefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self._token_repo.create(db_token)

        logger.info("User logged in: %s", user.email)
        return user, access_token, refresh_token

    async def google_auth(
        self,
        email: str,
        full_name: str,
        role: UserRole = UserRole.ADMIN,
    ) -> tuple[User, str, str]:
        """
        Authenticate or auto-register a user via Google Single Sign-On with requested RBAC role.
        """
        user = await self._user_repo.get_by_email(email)
        if user is None:
            user = User(
                email=email.lower().strip(),
                hashed_password=hash_password(str(uuid.uuid4())),
                full_name=full_name.strip() or "Google User",
                role=role,
                is_active=True,
                is_superuser=(role == UserRole.ADMIN),
            )
            user = await self._user_repo.create(user)
            logger.info("New Google user auto-registered: %s (role: %s)", user.email, user.role.value)
        elif user.role != role:
            # Update user role if changed
            user = await self._user_repo.update(user, {"role": role, "is_superuser": (role == UserRole.ADMIN)})

        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        await self._user_repo.update(user, {"last_login_at": datetime.now(timezone.utc)})

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value},
        )
        refresh_token, jti, expires_at = create_refresh_token(subject=str(user.id))

        db_token = UserRefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self._token_repo.create(db_token)
        logger.info("Google user logged in: %s (role: %s)", user.email, user.role.value)
        return user, access_token, refresh_token

    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        """
        Exchange a valid refresh token for new access + refresh tokens.

        Returns:
            Tuple of (new_access_token, new_refresh_token).

        Raises:
            TokenException: If the refresh token is invalid, expired, or revoked.
            EntityNotFoundException: If the user no longer exists.
            AuthenticationException: If the user account is deactivated.
        """
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise TokenException("Token is not a refresh token")

        user_id = payload.get("sub")
        jti = payload.get("jti")
        if user_id is None or jti is None:
            raise TokenException("Token payload missing subject or JTI claim")

        # Validate token against JTI in database
        db_token = await self._token_repo.get_by_jti(jti)
        if db_token is None or db_token.is_revoked or db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise TokenException("Token is expired, revoked, or invalid")

        user = await self._user_repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise EntityNotFoundException("User", user_id)

        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        # Revoke the old refresh token
        await self._token_repo.revoke_by_jti(jti)

        # Issue new tokens
        new_access = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value},
        )
        new_refresh, new_jti, new_expires = create_refresh_token(subject=str(user.id))

        # Persist new JTI
        new_db_token = UserRefreshToken(
            user_id=user.id,
            jti=new_jti,
            expires_at=new_expires,
            is_revoked=False,
        )
        await self._token_repo.create(new_db_token)

        return new_access, new_refresh

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        """Revoke a refresh token by parsing its JTI and marking it revoked in DB."""
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                await self._token_repo.revoke_by_jti(jti)
                logger.info("Revoked refresh token JTI: %s", jti)
        except TokenException:
            # Token is already invalid, no further action needed
            pass

    async def get_current_user(self, token: str) -> User:
        """
        Resolve the current user from an access token.

        Raises:
            TokenException: If the token is invalid.
            EntityNotFoundException: If the user no longer exists.
            AuthenticationException: If the user is deactivated.
        """
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise TokenException("Token is not an access token")

        user_id = payload.get("sub")
        if user_id is None:
            raise TokenException("Token payload missing subject")

        user = await self._user_repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise EntityNotFoundException("User", user_id)

        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        return user

    get_current_user_from_token = get_current_user
