"""
Sentinel AI — User Schemas

Request and response models for user CRUD operations.
Separates read (response) from write (request) schemas
to prevent mass-assignment vulnerabilities.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserResponse(BaseModel):
    """User data returned in API responses. Never exposes hashed_password."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """PATCH /users/{id} — Admin-only user update. All fields optional."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


class UserProfileUpdateRequest(BaseModel):
    """PATCH /auth/me — Self-service profile update (non-privileged fields)."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)


class UserListFilters(BaseModel):
    """Query filters for the user listing endpoint."""

    role: UserRole | None = None
    is_active: bool | None = None
    search: str | None = Field(
        default=None,
        max_length=255,
        description="Search by email or name (case-insensitive partial match)",
    )
