"""
Sentinel AI — Refresh Token Repository

Data access layer for UserRefreshToken entities.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import UserRefreshToken
from app.repositories.base import BaseRepository


class UserRefreshTokenRepository(BaseRepository[UserRefreshToken]):
    """Data access layer for tracking and revoking refresh tokens."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserRefreshToken, session)

    async def get_by_jti(self, jti: str) -> UserRefreshToken | None:
        """Fetch a token record by its unique JTI identifier."""
        result = await self._session.execute(
            select(UserRefreshToken).where(UserRefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke_by_jti(self, jti: str) -> None:
        """Revoke a specific refresh token by its JTI."""
        token = await self.get_by_jti(jti)
        if token:
            token.is_revoked = True
            await self._session.flush()

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens associated with a given user ID."""
        result = await self._session.execute(
            select(UserRefreshToken).where(
                UserRefreshToken.user_id == user_id,
                UserRefreshToken.is_revoked.is_(False),
            )
        )
        active_tokens = result.scalars().all()
        for token in active_tokens:
            token.is_revoked = True
        await self._session.flush()

    async def clean_expired_tokens(self) -> None:
        """Delete or mark as revoked all expired tokens."""
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(UserRefreshToken).where(
                UserRefreshToken.expires_at < now,
                UserRefreshToken.is_revoked.is_(False),
            )
        )
        expired_tokens = result.scalars().all()
        for token in expired_tokens:
            token.is_revoked = True
        await self._session.flush()
