"""Type definitions for response patterns.

This module defines the structure of different response types using TypedDict
for better type safety and IDE support.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union


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

    results: List[Any]
    pagination: PaginationInfo
    metadata: Optional[Dict[str, Any]]


class DetailResponse(TypedDict, total=False):
    """Response structure for single item details."""

    data: Any
    related: Optional[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]


class CollectionResponse(TypedDict, total=False):
    """Response structure for grouped collections."""

    collections: Dict[str, List[Any]]
    metadata: Optional[Dict[str, Any]]


class SearchFacet(TypedDict, total=False):
    """Search facet information."""

    name: str
    values: List[Dict[str, Union[str, int]]]


class SearchResponse(TypedDict, total=False):
    """Response structure for search results."""

    query: str
    results: List[Any]
    facets: Optional[Dict[str, SearchFacet]]
    suggestions: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]


class ActionResponse(TypedDict, total=False):
    """Response structure for action results (POST/PUT/DELETE)."""

    success: bool
    action: str
    data: Optional[Any]
    message: Optional[str]
    metadata: Optional[Dict[str, Any]]


class ErrorDetail(TypedDict, total=False):
    """Error detail information."""

    field: Optional[str]
    code: str
    message: str
    value: Optional[Any]


class ErrorInfo(TypedDict, total=False):
    """Error information structure."""

    code: str
    message: str
    details: Optional[List[ErrorDetail]]
    suggestions: Optional[List[str]]


class ErrorResponse(TypedDict, total=False):
    """Response structure for errors."""

    error: ErrorInfo
    metadata: Optional[Dict[str, Any]]
