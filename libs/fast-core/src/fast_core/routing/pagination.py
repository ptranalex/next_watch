"""Pagination utilities for FastAPI routing.

This module provides pagination utilities and helpers for FastAPI routes
to standardize pagination across the application.
"""

from typing import Any, Dict, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

from ..errors.responses import create_paginated_response

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters model."""

    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.page_size

    @property
    def skip(self) -> int:
        """Get skip value (alias for offset)."""
        return self.offset


class PaginationMeta(BaseModel):
    """Pagination metadata model."""

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResult(BaseModel):
    """Paginated result model."""

    data: List[Any] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
) -> PaginationParams:
    """Get pagination parameters from query parameters.

    Args:
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        PaginationParams instance
    """
    return PaginationParams(page=page, page_size=page_size)


def paginate_results(
    data: List[Any],
    pagination: PaginationParams,
    total_items: int,
) -> Dict[str, Any]:
    """Paginate results and create response.

    Args:
        data: List of items for current page
        pagination: Pagination parameters
        total_items: Total number of items across all pages

    Returns:
        Dictionary containing paginated response
    """
    return create_paginated_response(
        data=data,
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
    )


def calculate_pagination_meta(
    page: int,
    page_size: int,
    total_items: int,
) -> PaginationMeta:
    """Calculate pagination metadata.

    Args:
        page: Current page number
        page_size: Number of items per page
        total_items: Total number of items

    Returns:
        PaginationMeta instance
    """
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1

    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )


class Paginator:
    """Utility class for handling pagination."""

    def __init__(self, default_page_size: int = 20, max_page_size: int = 100):
        """Initialize paginator.

        Args:
            default_page_size: Default number of items per page
            max_page_size: Maximum allowed page size
        """
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size

    def get_params(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PaginationParams:
        """Get pagination parameters with validation.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            PaginationParams instance
        """
        page = max(1, page or 1)
        page_size = min(self.max_page_size, max(1, page_size or self.default_page_size))

        return PaginationParams(page=page, page_size=page_size)

    def paginate(
        self,
        data: List[Any],
        total_items: int,
        pagination: PaginationParams,
    ) -> PaginatedResult:
        """Create paginated result.

        Args:
            data: List of items for current page
            total_items: Total number of items
            pagination: Pagination parameters

        Returns:
            PaginatedResult instance
        """
        meta = calculate_pagination_meta(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_items,
        )

        return PaginatedResult(data=data, pagination=meta)


***REMOVED*** Default paginator instance
default_paginator = Paginator()


def get_page_links(
    base_url: str,
    pagination: PaginationParams,
    total_items: int,
) -> Dict[str, Optional[str]]:
    """Generate pagination links.

    Args:
        base_url: Base URL for pagination links
        pagination: Pagination parameters
        total_items: Total number of items

    Returns:
        Dictionary with pagination links
    """
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size

    links = {
        "self": f"{base_url}?page={pagination.page}&page_size={pagination.page_size}",
        "first": f"{base_url}?page=1&page_size={pagination.page_size}",
        "last": (
            f"{base_url}?page={total_pages}&page_size={pagination.page_size}"
            if total_pages > 0
            else None
        ),
        "next": None,
        "prev": None,
    }

    if pagination.page < total_pages:
        links["next"] = f"{base_url}?page={pagination.page + 1}&page_size={pagination.page_size}"

    if pagination.page > 1:
        links["prev"] = f"{base_url}?page={pagination.page - 1}&page_size={pagination.page_size}"

    return links


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100) -> tuple:
    """Validate and normalize pagination parameters.

    Args:
        page: Page number
        page_size: Page size
        max_page_size: Maximum allowed page size

    Returns:
        Tuple of (normalized_page, normalized_page_size)
    """
    normalized_page = max(1, page)
    normalized_page_size = min(max_page_size, max(1, page_size))

    return normalized_page, normalized_page_size
