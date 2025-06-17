"""
from backend_api.config.logging import get_logger
Error handling middleware for FastAPI.

This module provides a middleware that catches application-level exceptions
and converts them to standardized HTTP responses.
"""

from typing import Any, Awaitable, Callable, Dict, Optional, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend_api.errors import (
    ConflictError,
    PermissionError,
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
    service_error_to_http_exception,
)
from backend_api.config.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle application-level exceptions.

    This middleware catches exceptions from the service layer and
    converts them to standardized HTTP responses.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Union[JSONResponse, Any]:
        """
        Process a request and handle any exceptions.

        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler

        Returns:
            Either a JSON response for errors or the normal response
        """
        try:
            return await call_next(request)
        except ServiceError as e:
            ***REMOVED*** Convert service errors to HTTP exceptions
            http_exception = service_error_to_http_exception(e)

            ***REMOVED*** Log the error
            logger.error(
                f"Service error: {e.__class__.__name__} - {e.message}",
                extra={
                    "request_path": request.url.path,
                    "error_details": e.details,
                    "error_type": e.__class__.__name__,
                },
                exc_info=True,
            )

            ***REMOVED*** Return standardized response
            return JSONResponse(
                status_code=http_exception.status_code,
                content=http_exception.detail,
            )
        except Exception as e:
            ***REMOVED*** Handle unexpected errors
            logger.exception(
                f"Unhandled exception in request: {str(e)}",
                extra={"request_path": request.url.path},
            )

            ***REMOVED*** Return a generic server error
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred",
                    "details": ({"error": str(e)} if "debug" in request.query_params else {}),
                },
            )
