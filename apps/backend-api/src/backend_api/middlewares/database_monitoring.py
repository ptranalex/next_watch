"""Database monitoring middleware for FastAPI."""

import time
from typing import Callable, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.logging import get_logger
from backend_api.core.request_context import (
    set_request_context,
    get_request_context,
    clear_request_context,
)

logger = get_logger(__name__)


class DatabaseMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track database queries per request."""

    def __init__(self, app: Any, log_all_requests: bool = True):
        """Initialize the middleware.

        Args:
            app: FastAPI application
            log_all_requests: Whether to log all requests or only those with queries
        """
        super().__init__(app)
        self.log_all_requests = log_all_requests

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Process request and track database usage.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response with added timing headers
        """
        start_time = time.perf_counter()

        ***REMOVED*** Extract user info if available (you can customize this)
        user_id = self._extract_user_id(request)

        ***REMOVED*** Set request context
        context = set_request_context(
            method=request.method,
            path=str(request.url.path),
            user_id=user_id,
            start_time=start_time,
        )

        try:
            ***REMOVED*** Process the request
            response = await call_next(request)

            ***REMOVED*** Calculate total request duration
            total_duration_ms = (time.perf_counter() - start_time) * 1000

            ***REMOVED*** Get final context with query count
            final_context = get_request_context()
            query_count = final_context.query_count if final_context else 0

            ***REMOVED*** Log request summary
            self._log_request_summary(
                context=final_context,
                total_duration_ms=total_duration_ms,
                status_code=response.status_code,
            )

            ***REMOVED*** Add debugging headers in development
            if hasattr(request.app.state, "config") and getattr(
                request.app.state.config, "debug", False
            ):
                response.headers["X-DB-Query-Count"] = str(query_count)
                response.headers["X-Request-Duration-Ms"] = f"{total_duration_ms:.2f}"
                response.headers["X-Request-ID"] = context.request_id

            return response

        except Exception as e:
            ***REMOVED*** Log error with context
            total_duration_ms = (time.perf_counter() - start_time) * 1000
            final_context = get_request_context()

            logger.error(
                "Request failed with exception",
                exception=str(e),
                exception_type=type(e).__name__,
                total_duration_ms=round(total_duration_ms, 2),
                **(final_context.__dict__ if final_context else {}),
            )
            raise

        finally:
            ***REMOVED*** Always clear context
            clear_request_context()

    def _extract_user_id(self, request: Request) -> str | None:
        """Extract user ID from request (customize this for your auth system).

        Args:
            request: FastAPI request

        Returns:
            User ID if available, None otherwise
        """
        ***REMOVED*** Example: Extract from JWT token, session, etc.
        ***REMOVED*** For now, just check for a simple header
        return request.headers.get("X-User-ID")

    def _log_request_summary(
        self,
        context: Any,
        total_duration_ms: float,
        status_code: int,
    ) -> None:
        """Log request summary with database statistics.

        Args:
            context: Request context
            total_duration_ms: Total request duration
            status_code: HTTP status code
        """
        if context is None:
            return

        query_count = context.query_count

        ***REMOVED*** Determine if we should log this request
        should_log = (
            self.log_all_requests
            or query_count > 0
            or total_duration_ms > 1000  ***REMOVED*** Log slow requests
            or status_code >= 400  ***REMOVED*** Log error responses
        )

        if not should_log:
            return

        ***REMOVED*** Choose log level based on performance with structured logging
        if total_duration_ms > 2000 or query_count > 10:
            ***REMOVED*** Slow request or too many queries
            logger.warning(
                "Slow request detected",
                request_id=context.request_id,
                method=context.method,
                path=context.path,
                user_id=context.user_id,
                status_code=status_code,
                total_duration_ms=round(total_duration_ms, 2),
                db_query_count=query_count,
                slow_request=True,
            )
        elif status_code >= 400:
            ***REMOVED*** Error response
            logger.warning(
                "Request completed with error",
                request_id=context.request_id,
                method=context.method,
                path=context.path,
                user_id=context.user_id,
                status_code=status_code,
                total_duration_ms=round(total_duration_ms, 2),
                db_query_count=query_count,
                error_response=True,
            )
        else:
            ***REMOVED*** Normal request
            logger.info(
                "Request completed",
                request_id=context.request_id,
                method=context.method,
                path=context.path,
                user_id=context.user_id,
                status_code=status_code,
                total_duration_ms=round(total_duration_ms, 2),
                db_query_count=query_count,
            )
