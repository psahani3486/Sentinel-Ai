"""
Sentinel AI — Authentication Endpoints

Handles user registration, login, token refresh, and profile retrieval.
All business logic is delegated to AuthService.
"""

from fastapi import APIRouter, Cookie, Request, Response

from app.config.settings import get_settings
from app.core.dependencies import AuthSvc, CurrentUser
from app.core.exceptions import TokenException
from app.core.limiter import limiter
from app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import ErrorResponse, MessageResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    # Secure flag set only in production and non-test environments
    is_secure = settings.is_production and settings.ENVIRONMENT.lower() not in ("testing", "test") and not settings.DEBUG
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="strict",
        path="/api/v1/auth",  # Scoped to auth paths only for minimal exposure
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Google Single Sign-On / Registration",
    description="Authenticates or registers a user via Google OAuth.",
)
async def google_auth(
    request: Request,
    response: Response,
    body: GoogleAuthRequest,
    auth_service: AuthSvc,
) -> TokenResponse:
    user, access_token, refresh_token = await auth_service.google_auth(
        email=body.email,
        full_name=body.full_name,
        role=body.role,
    )
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token="",
        token_type="bearer",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account with specified RBAC role.",
    responses={
        409: {"model": ErrorResponse, "description": "Email already registered"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
@limiter.limit(get_settings().AUTH_RATE_LIMIT)
async def register(
    request: Request,
    body: RegisterRequest,
    auth_service: AuthSvc,
) -> UserResponse:
    user = await auth_service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        role=body.role,
    )
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain tokens",
    description="Validates credentials, returns access token, and sets refresh token cookie.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials or inactive account"},
    },
)
@limiter.limit(get_settings().AUTH_RATE_LIMIT)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    auth_service: AuthSvc,
) -> TokenResponse:
    user, access_token, refresh_token = await auth_service.login(
        email=body.email,
        password=body.password,
    )
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token="",  # No longer expose refresh token in response payload
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchanges a valid refresh token cookie or JSON payload for a new access token.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    response: Response,
    auth_service: AuthSvc,
    body: RefreshTokenRequest | None = None,
    refresh_token: str | None = Cookie(default=None),
) -> TokenResponse:
    token_str = (body.refresh_token if body and body.refresh_token else None) or refresh_token
    if not token_str:
        raise TokenException("Refresh token is missing")

    access_token, new_refresh_token = await auth_service.refresh_tokens(
        refresh_token=token_str,
    )
    _set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token if (body and body.refresh_token) else "",
        token_type="bearer",
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Revokes the active refresh token and clears the authentication cookie.",
)
async def logout(
    response: Response,
    auth_service: AuthSvc,
    refresh_token: str | None = Cookie(default=None),
) -> MessageResponse:
    if refresh_token:
        await auth_service.revoke_refresh_token(refresh_token)

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(current_user)
