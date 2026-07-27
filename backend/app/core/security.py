"""
Sentinel AI — Security Utilities

Provides password hashing (bcrypt) and JWT token management.
All token operations are pure functions — no DB or HTTP coupling.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.core.exceptions import TokenException

import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password Hashing ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ───────────────────────────────────────────────────────────────

def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a short-lived access token.

    Args:
        subject: The token subject (typically user ID as string).
        extra_claims: Additional claims to embed (e.g., role).

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims: dict[str, Any] = {
        "sub": subject,
        "exp": expires,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    if extra_claims:
        claims.update(extra_claims)

    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, jti: str | None = None) -> tuple[str, str, datetime]:
    """
    Create a long-lived refresh token.

    Args:
        subject: The token subject (typically user ID as string).
        jti: Optional unique identifier for the token. Generates a new UUID if not provided.

    Returns:
        Tuple of (encoded_jwt_string, jti_string, expires_datetime).
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_jti = jti or str(uuid.uuid4())

    claims: dict[str, Any] = {
        "sub": subject,
        "exp": expires,
        "iat": now,
        "jti": token_jti,
        "type": "refresh",
    }
    token = jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, token_jti, expires


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: The encoded JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        TokenException: If the token is invalid or expired.
    """
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if "sub" not in payload:
            raise TokenException(message="Token payload missing 'sub' claim")
        return payload
    except JWTError as exc:
        raise TokenException(message=f"Token validation failed: {exc}") from exc
