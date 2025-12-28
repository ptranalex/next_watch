"""Type definitions for response patterns.

This module defines the structure of different response types using TypedDict
for better type safety and IDE support.
"""

from typing import Any, TypedDict


class PaginationInfo(TypedDict, total=False):
    """Pagination metadata."""

    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(TypedDict, total=False):
    """Response structure for paginated data."""

    results: list[Any]
    pagination: PaginationInfo
    metadata: dict[str, Any] | None


class DetailResponse(TypedDict, total=False):
    """Response structure for single item details."""

    data: Any
    related: dict[str, Any] | None
    context: dict[str, Any] | None
    metadata: dict[str, Any] | None


class CollectionResponse(TypedDict, total=False):
    """Response structure for grouped collections."""

    collections: dict[str, list[Any]]
    metadata: dict[str, Any] | None


class SearchFacet(TypedDict, total=False):
    """Search facet information."""

    name: str
    values: list[dict[str, str | int]]


class SearchResponse(TypedDict, total=False):
    """Response structure for search results."""

    query: str
    results: list[Any]
    facets: dict[str, SearchFacet] | None
    suggestions: list[str] | None
    metadata: dict[str, Any] | None


class ActionResponse(TypedDict, total=False):
    """Response structure for action results (POST/PUT/DELETE)."""

    success: bool
    action: str
    data: Any | None
    message: str | None
    metadata: dict[str, Any] | None


class ErrorDetail(TypedDict, total=False):
    """Error detail information."""

    field: str | None
    code: str
    message: str
    value: Any | None


class ErrorInfo(TypedDict, total=False):
    """Error information structure."""

    code: str
    message: str
    details: list[ErrorDetail] | None
    suggestions: list[str] | None


class ErrorResponse(TypedDict, total=False):
    """Response structure for errors."""

    error: ErrorInfo
    metadata: dict[str, Any] | None
