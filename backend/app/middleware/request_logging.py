"""
Sentinel AI — Request Logging Middleware

Logs every incoming request and outgoing response with timing.
Adds a unique request_id for correlation across log entries.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("sentinel.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs request/response details with timing.

    Adds X-Request-ID header for distributed tracing correlation.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Attach request_id to request state for downstream use
        request.state.request_id = request_id

        logger.info(
            "→ %s %s (request_id=%s, client=%s)",
            request.method,
            request.url.path,
            request_id,
            request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "✗ %s %s → 500 (%.1fms, request_id=%s)",
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            "← %s %s → %d (%.1fms, request_id=%s)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response
