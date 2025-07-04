"""Logging middleware for FastAPI applications.

This module provides logging middleware that adds request/response logging
with configurable detail levels and structured logging support.
"""

import time
import uuid
from typing import Any, Callable, List, Optional, cast

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(
        self,
        app: ASGIApp,
        log_requests: bool = True,
        log_responses: bool = True,
        include_headers: bool = False,
        include_body: bool = False,
        max_body_size: int = 1024,
        exclude_paths: Optional[List[str]] = None,
        level: str = "INFO",
    ):
        """Initialize logging middleware.

        Args:
            app: FastAPI application
            log_requests: Whether to log incoming requests
            log_responses: Whether to log outgoing responses
            include_headers: Whether to include headers in logs
            include_body: Whether to include request/response bodies
            max_body_size: Maximum body size to log (bytes)
            exclude_paths: List of paths to exclude from logging
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.include_headers = include_headers
        self.include_body = include_body
        self.max_body_size = max_body_size
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
        self.level = level.upper()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and response.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response from the application
        """
        ***REMOVED*** Generate request ID if not present
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        ***REMOVED*** Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return cast(Response, response)

        start_time = time.time()

        ***REMOVED*** Log request
        if self.log_requests:
            await self._log_request(request, request_id)

        ***REMOVED*** Process request
        response = await call_next(request)

        ***REMOVED*** Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

        ***REMOVED*** Log response
        if self.log_responses:
            await self._log_response(request, response, request_id, process_time)

        return cast(Response, response)

    async def _log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request.

        Args:
            request: Incoming request
            request_id: Request ID
        """
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
        }

        if self.include_headers:
            log_data["headers"] = dict(request.headers)

        if self.include_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    log_data["body"] = body.decode("utf-8")
                else:
                    log_data["body"] = f"<truncated, size: {len(body)} bytes>"
            except Exception as e:
                log_data["body_error"] = str(e)

        ***REMOVED*** Log with configured level
        if self.level == "DEBUG":
            logger.debug("Incoming request", **log_data)
        elif self.level == "WARNING":
            logger.warning("Incoming request", **log_data)
        elif self.level == "ERROR":
            logger.error("Incoming request", **log_data)
        else:
            logger.info("Incoming request", **log_data)

    async def _log_response(
        self, request: Request, response: Response, request_id: str, process_time: float
    ) -> None:
        """Log outgoing response.

        Args:
            request: Original request
            response: Outgoing response
            request_id: Request ID
            process_time: Processing time in seconds
        """
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
        }

        if self.include_headers:
            log_data["response_headers"] = dict(response.headers)

        ***REMOVED*** Log level based on status code
        if response.status_code >= 500:
            logger.error("Response sent", **log_data)
        elif response.status_code >= 400:
            logger.warning("Response sent", **log_data)
        else:
            logger.info("Response sent", **log_data)


def setup_logging(app: FastAPI, settings: Any) -> None:
    """Set up logging middleware for FastAPI application.

    Args:
        app: FastAPI application
        settings: Application settings
    """
    ***REMOVED*** Get logging configuration from settings
    log_requests = getattr(settings, "log_requests", True)
    log_responses = getattr(settings, "log_responses", True)
    include_headers = getattr(settings, "log_include_headers", False)
    include_body = getattr(settings, "log_include_body", False)
    max_body_size = getattr(settings, "log_max_body_size", 1024)
    exclude_paths = getattr(settings, "log_exclude_paths", None)

    ***REMOVED*** Add logging middleware
    ***REMOVED*** Type ignore due to FastAPI middleware registration type annotation issue
    app.add_middleware(
        LoggingMiddleware,
        log_requests=log_requests,
        log_responses=log_responses,
        include_headers=include_headers,
        include_body=include_body,
        max_body_size=max_body_size,
        exclude_paths=exclude_paths,
    )

    logger.info("Logging middleware configured")


def get_request_logger(request: Request) -> Any:
    """Get logger with request context.

    Args:
        request: HTTP request

    Returns:
        Structlog logger bound with request context
    """
    request_id = request.headers.get("X-Request-ID", "unknown")

    ***REMOVED*** Create logger with context
    context_logger = logger.bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client=getattr(request.client, "host", "unknown") if request.client else "unknown",
    )

    return context_logger
