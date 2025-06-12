"""Logging middleware for BFF application with structured logging."""

import time
from typing import Callable, Awaitable, cast
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from bff_api.config.logging import get_logger

logger = get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses with structured logging."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and log details.

        Args:
            request: FastAPI request
            call_next: Next middleware function

        Returns:
            Response from next middleware/endpoint
        """
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"

        ***REMOVED*** Log request with structured data
        logger.info(
            "HTTP request received",
            method=request.method,
            path=request.url.path,
            client_host=client_host,
            query_params=str(request.query_params) if request.query_params else None,
        )

        ***REMOVED*** Process request
        response = await call_next(request)

        ***REMOVED*** Calculate duration
        duration = time.time() - start_time

        ***REMOVED*** Log response with structured data
        logger.info(
            "HTTP response sent",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_seconds=round(duration, 3),
            client_host=client_host,
        )

        return response
