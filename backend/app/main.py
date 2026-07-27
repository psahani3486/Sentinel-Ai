"""
Sentinel AI — FastAPI Application Factory

Production entry point configuring:
1. Structured logging.
2. Production OpenAPI metadata.
3. Security middleware (GZip, Trusted Host, CORS, Security Headers, Request Size Limit).
4. Global exception handlers & Rate limiting.
5. Versioned API router mounting & Root health probes.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_v1_router
from app.config.logging_config import setup_logging
from app.config.settings import get_settings
from app.core.limiter import limiter
from app.db.init_db import init_db
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logging import RequestLoggingMiddleware

# Setup production logging
setup_logging()
logger = logging.getLogger(__name__)


# ── Production Security Headers Middleware ────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects production HTTP security headers into all API responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        settings = get_settings()
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# ── Production Request Size Limit Middleware ──────────────────────────────────
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforces 10MB maximum payload size limit on incoming requests."""

    def __init__(self, app, max_bytes: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_bytes:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"error": "payload_too_large", "message": "Request payload exceeds 10MB limit."},
            )
        return await call_next(request)


# ── Lifespan Context Manager ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown hooks."""
    settings = get_settings()
    logger.info("Starting %s v%s [%s]", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)

    # Initialize DB (seed initial data)
    try:
        await init_db()
        logger.info("Database initialization complete.")
    except Exception as e:
        logger.warning("Database startup check skipped or failed: %s", str(e))

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


# ── FastAPI App Factory ───────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """Create and configure production FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Rate Limiting
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "details": {"limit": str(exc.detail)},
            },
        )

    # Root Level Cloud Health Probes
    @app.get("/health", include_in_schema=False)
    @app.get("/readiness", include_in_schema=False)
    @app.get("/liveness", include_in_schema=False)
    async def root_health_probe():
        return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    # Middleware Stack (Outer to Inner)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts_list,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # Register Exception Handlers
    register_exception_handlers(app)

    # Mount API Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


# Application Instance
app = create_app()
