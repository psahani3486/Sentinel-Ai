"""
Sentinel AI — Refresh Token Model

Defines the database-backed tracking of active refresh tokens.
Supports revocation check by JTI. Highly compatible with a future
Redis blacklist/allowlist transition.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRefreshToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Tracks issued refresh tokens via their unique JTI (JWT ID).

    If a token's is_revoked is set to True, or the current time is past
    expires_at, the session is invalidated.
    """

    __tablename__ = "user_refresh_tokens"

    __table_args__ = (
        Index("ix_user_refresh_tokens_jti", "jti", unique=True),
        Index("ix_user_refresh_tokens_is_revoked", "is_revoked"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jti: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="refresh_tokens")

    def __repr__(self) -> str:
        return f"<UserRefreshToken(jti={self.jti}, user_id={self.user_id}, revoked={self.is_revoked})>"
