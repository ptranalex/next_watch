"""Common dependency providers for FastAPI applications.

This module provides basic dependency providers that are commonly used
across FastAPI applications.
"""

import uuid
from typing import Any, Callable, Dict, Optional

from config.logging import get_logger
from fastapi import Depends, Query, Request

logger = get_logger(__name__)


def get_settings() -> Any:
    """Get application settings from app state.

    Returns:
        Dependency function that returns application settings

    Raises:
        RuntimeError: If settings not found in app state
    """

    def _get_settings(request: Request) -> Any:
        settings = getattr(request.app.state, "settings", None)
        if settings is None:
            raise RuntimeError("Settings not found in app state")
        return settings

    return Depends(_get_settings)


def get_request_id() -> Any:
    """Get or generate a request ID for tracking.

    Returns:
        Dependency function that returns request ID
    """

    def _get_request_id(request: Request) -> str:
        ***REMOVED*** Try to get request ID from headers
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            ***REMOVED*** Generate a new request ID
            request_id = str(uuid.uuid4())

        ***REMOVED*** Store in request state for later use
        request.state.request_id = request_id
        return request_id

    return Depends(_get_request_id)


class PaginationParams:
    """Pagination parameters for queries."""

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
    ):
        """Initialize pagination parameters.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            max_page_size: Maximum allowed page size
        """
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size

    @property
    def skip(self) -> int:
        """Number of items to skip (alias for offset)."""
        return self.offset


def get_pagination(
    max_page_size: int = 100,
) -> Any:
    """Get pagination parameters from query parameters.

    Args:
        max_page_size: Maximum allowed page size

    Returns:
        Dependency function that returns PaginationParams
    """

    def _get_pagination(
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(20, ge=1, le=max_page_size, description="Number of items per page"),
    ) -> PaginationParams:
        return PaginationParams(
            page=page,
            page_size=page_size,
            max_page_size=max_page_size,
        )

    return Depends(_get_pagination)


def get_search_params(
    query: Optional[str] = Query(None, description="Search query"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
) -> Dict[str, Any]:
    """Get search and sorting parameters.

    Args:
        query: Search query string
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)

    Returns:
        Dictionary with search parameters
    """
    return {
        "query": query,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }
