"""BFF-specific error handling utilities built on Fast Core."""

from typing import Any

from config.logging import get_logger
from fast_core.errors import (
    ServiceErrorContext,
    create_error_response,
    handle_service_error,
    service_error_handler,
)
from fast_core.responses import ResponseBuilder

logger = get_logger(__name__)

# BFF-specific service error handlers
backend_error_handler = service_error_handler("backend-api", logger)
auth_error_handler = service_error_handler("auth-api", logger)
recommendation_error_handler = service_error_handler("recommendation-api", logger)
ml_error_handler = service_error_handler("ml-api", logger)


async def handle_backend_error(e: Exception, operation: str, **context: Any) -> None:
    """Handle backend service errors (BFF-specific wrapper).

    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        **context: Additional context for logging
    """
    handle_service_error(
        e=e, operation=operation, service_name="backend-api", logger=logger, **context
    )


def create_bff_error_response(
    responses: ResponseBuilder,
    page: int,
    limit: int,
    collection_type: str,
    error_message: str = "Backend service unavailable",
    user_id: int | None = None,
    **metadata_extras: Any,
) -> Any:
    """Create BFF-specific error response.

    Args:
        responses: ResponseBuilder instance
        page: Page number for pagination
        limit: Items per page
        collection_type: Type of collection (e.g., "liked_movies", "top_movies")
        error_message: Error message to include
        user_id: Optional user ID for context
        **metadata_extras: Additional metadata to include

    Returns:
        Paginated response with BFF-specific error information
    """
    return create_error_response(
        responses=responses,
        page=page,
        limit=limit,
        collection_type=collection_type,
        service_names=["backend-api"],
        error_message=error_message,
        user_id=user_id,
        **metadata_extras,
    )


# Removed: build_backend_path - now handled by ServiceClient


class BackendErrorContext(ServiceErrorContext):
    """Context manager for backend service errors."""

    def __init__(self, operation: str, **context: Any):
        super().__init__(service_name="backend-api", operation=operation, logger=logger, **context)
