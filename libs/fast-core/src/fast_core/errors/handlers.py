"""Generic error handling utilities for FastAPI applications."""

import functools
import re
from typing import Any, Callable, Dict, Optional, TypeVar, Union

import httpx
from fastapi import HTTPException
from fast_core.errors.exceptions import ExternalServiceException
from fast_core.responses import ResponseBuilder

F = TypeVar("F", bound=Callable[..., Any])


def handle_service_error(
    e: Exception, operation: str, service_name: str, logger: Any, **context: Any
) -> None:
    """Handle external service errors consistently.

    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        service_name: Name of the external service
        logger: Logger instance to use
        **context: Additional context for logging

    Raises:
        HTTPException: For specific HTTP status codes (401, 404)
        ExternalServiceException: For general service unavailability
    """
    logger.error(
        f"Service error for {operation}",
        error=str(e),
        service=service_name,
        endpoint=operation,
        **context,
    )

    ***REMOVED*** Handle specific HTTP status codes
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Authentication failed")
        elif e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found")
        elif e.response.status_code == 403:
            raise HTTPException(status_code=403, detail="Access forbidden")
        elif e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    ***REMOVED*** Default to service unavailable
    raise ExternalServiceException(
        detail=f"{service_name} service unavailable",
        service_name=service_name,
        error_code="SERVICE_UNAVAILABLE",
    )


def create_error_response(
    responses: ResponseBuilder,
    page: int,
    limit: int,
    collection_type: str,
    service_names: Optional[list[str]] = None,
    error_message: str = "Service unavailable",
    user_id: Optional[int] = None,
    **metadata_extras: Any,
) -> Any:
    """Create a consistent paginated error response.

    Args:
        responses: ResponseBuilder instance
        page: Page number for pagination
        limit: Items per page
        collection_type: Type of collection (e.g., "liked_movies", "top_movies")
        service_names: List of service names that were unavailable
        error_message: Error message to include
        user_id: Optional user ID for context
        **metadata_extras: Additional metadata to include

    Returns:
        Paginated response with error information
    """
    metadata = {
        "error": error_message,
        "service_info": {"aggregated_from": service_names or ["external-service"]},
        "api_version": "v1",
        "response_pattern": "paginated",
        "collection_type": collection_type,
    }

    if user_id:
        metadata["user_context"] = {"user_id": user_id}

    metadata.update(metadata_extras)

    return responses.paginated(
        items=[],
        page=page,
        limit=limit,
        total=0,
        metadata=metadata,
    )


def service_error_handler(
    service_name: str, logger: Any, operation_name: Optional[str] = None
) -> Callable[[F], F]:
    """Decorator for consistent service error handling.

    Args:
        service_name: Name of the external service
        logger: Logger instance to use
        operation_name: Optional operation name (defaults to function name)

    Returns:
        Decorator function

    Example:
        @service_error_handler("backend-api", logger)
        async def get_movies():
            ***REMOVED*** This will automatically handle service errors
            return await backend_client.get("/movies")
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                operation = operation_name or func.__name__
                handle_service_error(
                    e=e,
                    operation=operation,
                    service_name=service_name,
                    logger=logger,
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                )

        return wrapper  ***REMOVED*** type: ignore

    return decorator


***REMOVED*** Removed: build_api_path moved to fast_core.clients for better separation of concerns


class ServiceErrorContext:
    """Context manager for service error handling with automatic logging."""

    def __init__(self, service_name: str, operation: str, logger: Any, **context: Any):
        self.service_name = service_name
        self.operation = operation
        self.logger = logger
        self.context = context

    async def __aenter__(self) -> "ServiceErrorContext":
        self.logger.debug(f"Starting {self.operation} for {self.service_name}")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is not None:
            handle_service_error(
                e=exc_val,
                operation=self.operation,
                service_name=self.service_name,
                logger=self.logger,
                **self.context,
            )
        return False  ***REMOVED*** Don't suppress the exception
