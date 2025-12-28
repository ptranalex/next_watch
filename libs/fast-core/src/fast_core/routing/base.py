"""Base router implementation with enhanced functionality.

This module provides a BaseRouter class that extends FastAPI's APIRouter
with additional functionality and standardized patterns.
"""

from collections.abc import Callable, Sequence
from typing import Any

from config.logging import get_logger
from fastapi import APIRouter
from fastapi.routing import APIRoute

logger = get_logger(__name__)


class BaseRouter(APIRouter):
    """Base router with enhanced functionality.

    This router extends FastAPI's APIRouter with:
    - Standard responses for common status codes
    - Version prefix handling
    - Consistent error handling
    - Logging of route registration
    """

    def __init__(
        self,
        *,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: Sequence[Any] | None = None,
        responses: dict[int, dict[str, Any]] | None = None,
        route_class: type[APIRoute] = APIRoute,
        **kwargs: Any,
    ) -> None:
        """Initialize the router with enhanced defaults.

        Args:
            prefix: URL path prefix for all routes
            tags: OpenAPI tags for all routes
            dependencies: Dependencies for all routes
            responses: Response descriptions for all routes
            route_class: Custom route class
            **kwargs: Additional arguments for APIRouter
        """
        ***REMOVED*** Add standard responses for common status codes
        standard_responses: dict[int | str, dict[str, Any]] = {
            400: {"description": "Bad Request", "model": None},
            401: {"description": "Unauthorized", "model": None},
            403: {"description": "Forbidden", "model": None},
            404: {"description": "Not Found", "model": None},
            422: {"description": "Validation Error", "model": None},
            500: {"description": "Internal Server Error", "model": None},
        }

        ***REMOVED*** Merge with user-provided responses
        if responses:
            for status_code, response in responses.items():
                standard_responses[status_code] = response

        ***REMOVED*** Initialize with enhanced defaults
        super().__init__(
            prefix=prefix,
            tags=list(tags) if tags else None,
            dependencies=dependencies or [],
            responses=standard_responses,
            route_class=route_class,
            **kwargs,
        )

        logger.debug(f"Initialized router with prefix: {prefix}, tags: {tags}")

    def include_versioned_routes(
        self,
        router: APIRouter,
        prefix: str,
        version: int | str = 1,
    ) -> None:
        """Include routes with version prefix.

        Args:
            router: Router to include
            prefix: URL path prefix
            version: API version (default: 1)
        """
        version_str = f"v{version}" if isinstance(version, int) else version
        versioned_prefix = f"/{prefix}/{version_str}"

        self.include_router(router, prefix=versioned_prefix)
        logger.debug(f"Included versioned router at: {versioned_prefix}")

    def add_error_handler(self, exc_class: type[Exception], handler: Callable) -> None:
        """Add an error handler for a specific exception.

        This is a convenience method that adds the handler to the parent app
        when the router is included.

        Args:
            exc_class: Exception class to handle
            handler: Handler function
        """
        ***REMOVED*** Store handlers to be added when router is included in an app
        if not hasattr(self, "_error_handlers"):
            self._error_handlers = []

        self._error_handlers.append((exc_class, handler))
        logger.debug(f"Added error handler for: {exc_class.__name__}")
