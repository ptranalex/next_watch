"""Logging middleware for BFF application."""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details.

        Args:
            request: FastAPI request
            call_next: Next middleware function

        Returns:
            Response from next middleware/endpoint
        """
        start_time = time.time()

        ***REMOVED*** Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        ***REMOVED*** Process request
        response = await call_next(request)

        ***REMOVED*** Calculate duration
        duration = time.time() - start_time

        ***REMOVED*** Log response
        logger.info(
            f"Response: {response.status_code} "
            f"for {request.method} {request.url.path} "
            f"in {duration:.3f}s"
        )

        return response
