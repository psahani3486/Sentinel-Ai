"""
Sentinel AI — Global Exception Handler

Maps domain exceptions to HTTP status codes and returns
a standardized ErrorResponse JSON body. This is registered
as an exception handler on the FastAPI app.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    DuplicateEntityException,
    EntityNotFoundException,
    SentinelException,
    TokenException,
    ValidationException,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI application."""

    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(DuplicateEntityException)
    async def duplicate_entity_handler(
        request: Request, exc: DuplicateEntityException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": "conflict",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(AuthenticationException)
    async def authentication_handler(
        request: Request, exc: AuthenticationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": "authentication_failed",
                "message": exc.message,
            },
        )

    @app.exception_handler(AuthorizationException)
    async def authorization_handler(
        request: Request, exc: AuthorizationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "forbidden",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(TokenException)
    async def token_handler(request: Request, exc: TokenException) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": "token_error",
                "message": exc.message,
            },
        )

    @app.exception_handler(ValidationException)
    async def validation_handler(
        request: Request, exc: ValidationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error.get("loc", []))
            errors.append({
                "field": field,
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "unknown"),
            })
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": {"errors": errors},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": str(exc.detail),
            },
        )

    @app.exception_handler(SentinelException)
    async def sentinel_exception_handler(
        request: Request, exc: SentinelException
    ) -> JSONResponse:
        logger.error("Unhandled domain exception: %s", exc.message, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.critical("Unhandled exception: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )
