"""Pydantic schemas for API request/response validation."""

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import ErrorResponse, HealthResponse, PaginatedResponse
from app.schemas.dataset import (
    DatasetColumnCreate,
    DatasetColumnResponse,
    DatasetCreate,
    DatasetProfileCreate,
    DatasetProfileResponse,
    DatasetResponse,
    DatasetSchemaCreate,
    DatasetSchemaResponse,
    DatasetSummary,
    DatasetUpdate,
    DatasetVersionCreate,
    DatasetVersionResponse,
)
from app.schemas.user import (
    UserListFilters,
    UserProfileUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.schemas.validation import (
    ValidationResultCreate,
    ValidationResultResponse,
    ValidationRuleCreate,
    ValidationRuleResponse,
    ValidationRuleUpdate,
    ValidationRunCreate,
    ValidationRunResponse,
    ValidationRunSummary,
)

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
    "UserUpdateRequest",
    "UserProfileUpdateRequest",
    "UserListFilters",
    "DatasetCreate",
    "DatasetUpdate",
    "DatasetResponse",
    "DatasetSummary",
    "DatasetVersionCreate",
    "DatasetVersionResponse",
    "DatasetSchemaCreate",
    "DatasetSchemaResponse",
    "DatasetColumnCreate",
    "DatasetColumnResponse",
    "DatasetProfileCreate",
    "DatasetProfileResponse",
    "ValidationRuleCreate",
    "ValidationRuleUpdate",
    "ValidationRuleResponse",
    "ValidationRunCreate",
    "ValidationRunResponse",
    "ValidationRunSummary",
    "ValidationResultCreate",
    "ValidationResultResponse",
]
