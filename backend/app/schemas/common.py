"""
Sentinel AI — Common Schemas

Shared response schemas used across all API endpoints:
pagination, health checks, and standardized error responses.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ── Health ───────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """GET /health response."""

    status: str = Field(..., examples=["healthy"])
    version: str = Field(..., examples=["1.0.0"])
    environment: str = Field(..., examples=["development"])
    timestamp: datetime


class DBHealthResponse(HealthResponse):
    """GET /health/db response — includes database connectivity."""

    database: str = Field(..., examples=["connected"])


# ── Pagination ───────────────────────────────────────────────────────────────


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page",
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list response."""

    items: list[T]
    total: int = Field(..., description="Total number of matching records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


# ── Errors ───────────────────────────────────────────────────────────────────


class ErrorDetail(BaseModel):
    """Individual error detail within an error response."""

    field: str | None = None
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """Standardized error response returned by all endpoints."""

    error: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Any = Field(default=None, description="Additional error context")
    request_id: str | None = Field(
        default=None,
        description="Request correlation ID for debugging",
    )


# ── Generic ──────────────────────────────────────────────────────────────────


class MessageResponse(BaseModel):
    """Simple message response for operations that return no data."""

    message: str
    success: bool = True
