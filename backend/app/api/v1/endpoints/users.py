"""
Sentinel AI — User Management Endpoints

Admin-only CRUD operations for managing platform users.
All endpoints require ADMIN role via the RoleGuard dependency.
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, UserSvc, require_admin
from app.models.user import UserRole
from app.schemas.common import ErrorResponse, MessageResponse, PaginatedResponse
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users",
    description="Returns a paginated list of users. Supports filtering by role, "
    "active status, and free-text search on email/name.",
    responses={
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
    },
)
async def list_users(
    user_service: UserSvc,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    role: UserRole | None = Query(default=None, description="Filter by role"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    search: str | None = Query(default=None, max_length=255, description="Search email/name"),
) -> PaginatedResponse[UserResponse]:
    return await user_service.list_users(
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
        search=search,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns the details of a specific user.",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
    },
)
async def get_user(
    user_id: uuid.UUID,
    user_service: UserSvc,
) -> UserResponse:
    user = await user_service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user profile, role, or active status. "
    "Admins cannot demote themselves.",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        409: {"model": ErrorResponse, "description": "Email conflict"},
    },
)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdateRequest,
    user_service: UserSvc,
    current_user: CurrentUser,
) -> UserResponse:
    update_data = body.model_dump(exclude_unset=True)
    user = await user_service.update_user(user_id, update_data, current_user)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Deactivate user",
    description="Soft-deletes a user by setting is_active to false. "
    "Cannot deactivate yourself or the last active admin.",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Cannot deactivate self"},
        422: {"model": ErrorResponse, "description": "Last admin protection"},
    },
)
async def deactivate_user(
    user_id: uuid.UUID,
    user_service: UserSvc,
    current_user: CurrentUser,
) -> MessageResponse:
    await user_service.deactivate_user(user_id, current_user)
    return MessageResponse(message="User deactivated successfully")
