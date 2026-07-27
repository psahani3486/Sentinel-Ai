"""
Sentinel AI — Authentication Schemas

Request and response models for login, registration, and token operations.
"""

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class LoginRequest(BaseModel):
    """POST /auth/login request body."""

    email: EmailStr = Field(..., examples=["admin@sentinel-ai.io"])
    password: str = Field(..., min_length=8, max_length=128, examples=["ChangeMe123!"])


class RegisterRequest(BaseModel):
    """POST /auth/register request body."""

    email: EmailStr = Field(..., examples=["engineer@company.com"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Minimum 8 characters",
        examples=["SecureP@ss123"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Jane Smith"],
    )
    role: UserRole = Field(default=UserRole.VIEWER, description="User RBAC Role")


class TokenResponse(BaseModel):
    """Response containing JWT access and refresh tokens."""

    access_token: str = Field(..., description="Short-lived access token")
    refresh_token: str = Field(..., description="Long-lived refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")


class RefreshTokenRequest(BaseModel):
    """POST /auth/refresh request body."""

    refresh_token: str = Field(..., description="Valid refresh token to exchange")


class GoogleAuthRequest(BaseModel):
    """POST /auth/google request body."""

    email: EmailStr = Field(default="user@gmail.com", description="Google user email")
    full_name: str = Field(default="Google User", description="Google user full name")
    google_id: str | None = Field(default=None, description="Google OAuth ID")
    role: UserRole = Field(default=UserRole.ADMIN, description="User RBAC Role")

