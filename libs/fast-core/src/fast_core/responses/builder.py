"""Response builder for consistent API responses.

This module provides the ResponseBuilder class that creates consistent, well-structured
API responses using generic patterns that work across any domain.
"""

import math
from typing import Any

from .types import (
    ActionResponse,
    CollectionResponse,
    DetailResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationInfo,
    SearchResponse,
)


class ResponseBuilder:
    """Builder for creating consistent API responses.

    Provides methods for common response patterns like pagination, detail views,
    search results, collections, and error responses. All patterns are generic
    and work across any domain or service.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize response builder with optional configuration.

        Args:
            config: Optional configuration for default behavior
        """
        self.config = config or {}

        ***REMOVED*** Default configuration
        self._defaults: dict[str, dict[str, Any]] = {
            "pagination": {
                "default_limit": 20,
                "max_limit": 100,
                "include_total_pages": True,
                "include_has_next_prev": True,
            },
            "detail": {
                "include_timestamps": True,
                "include_metadata": True,
            },
            "search": {
                "include_suggestions": True,
                "include_facets": True,
            },
            "errors": {
                "include_suggestions": True,
                "include_details": True,
            },
        }

    def paginated(
        self,
        items: list[Any],
        page: int,
        limit: int,
        total: int,
        metadata: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> PaginatedResponse:
        """Create a paginated response.

        Args:
            items: List of items for current page
            page: Current page number (1-based)
            limit: Items per page
            total: Total number of items
            metadata: Optional additional metadata
            config_override: Override default configuration

        Returns:
            Structured paginated response
        """
        ***REMOVED*** Merge configuration
        pagination_config = {
            **self._defaults["pagination"],
            **(self.config.get("pagination") or {}),
        }
        if config_override:
            pagination_config.update(config_override)

        ***REMOVED*** Calculate pagination info
        total_pages = math.ceil(total / limit) if limit > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        ***REMOVED*** Build pagination metadata
        pagination_info: PaginationInfo = {
            "page": page,
            "per_page": limit,
            "total": total,
        }

        if pagination_config.get("include_total_pages", True):
            pagination_info["total_pages"] = total_pages

        if pagination_config.get("include_has_next_prev", True):
            pagination_info["has_next"] = has_next
            pagination_info["has_prev"] = has_prev

        response: PaginatedResponse = {
            "results": items,
            "pagination": pagination_info,
        }

        if metadata:
            response["metadata"] = metadata

        return response

    def detail(
        self,
        item: Any,
        related: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> DetailResponse:
        """Create a detail response for a single item.

        Args:
            item: The main item data
            related: Optional related items (e.g., cast, trailers, similar)
            context: Optional context data (e.g., user interactions)
            metadata: Optional additional metadata
            config_override: Override default configuration

        Returns:
            Structured detail response
        """
        response: DetailResponse = {
            "data": item,
        }

        if related:
            response["related"] = related

        if context:
            response["context"] = context

        if metadata:
            response["metadata"] = metadata

        return response

    def collection(
        self,
        groups: dict[str, list[Any]],
        metadata: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> CollectionResponse:
        """Create a collection response with grouped items.

        Args:
            groups: Dictionary of group names to item lists
            metadata: Optional additional metadata
            config_override: Override default configuration

        Returns:
            Structured collection response
        """
        response: CollectionResponse = {
            "collections": groups,
        }

        if metadata:
            response["metadata"] = metadata

        return response

    def search(
        self,
        query: str,
        results: list[Any],
        facets: dict[str, Any] | None = None,
        suggestions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> SearchResponse:
        """Create a search response.

        Args:
            query: The search query
            results: List of search results
            facets: Optional search facets/filters
            suggestions: Optional search suggestions
            metadata: Optional additional metadata
            config_override: Override default configuration

        Returns:
            Structured search response
        """
        ***REMOVED*** Merge configuration
        search_config = {
            **self._defaults["search"],
            **(self.config.get("search") or {}),
        }
        if config_override:
            search_config.update(config_override)

        response: SearchResponse = {
            "query": query,
            "results": results,
        }

        if facets and search_config.get("include_facets", True):
            response["facets"] = facets

        if suggestions and search_config.get("include_suggestions", True):
            response["suggestions"] = suggestions

        if metadata:
            response["metadata"] = metadata

        return response

    def action(
        self,
        success: bool,
        action: str,
        data: Any | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> ActionResponse:
        """Create an action response (for POST/PUT/DELETE operations).

        Args:
            success: Whether the action was successful
            action: Description of the action performed
            data: Optional data returned from the action
            message: Optional human-readable message
            metadata: Optional additional metadata
            config_override: Override default configuration

        Returns:
            Structured action response
        """
        response: ActionResponse = {
            "success": success,
            "action": action,
        }

        if data is not None:
            response["data"] = data

        if message:
            response["message"] = message

        if metadata:
            response["metadata"] = metadata

        return response

    def error(
        self,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
        suggestions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> ErrorResponse:
        """Create an error response.

        Args:
            code: Error code (e.g., "MOVIE_NOT_FOUND")
            message: Human-readable error message
            details: Optional detailed error information
            suggestions: Optional suggestions for resolving the error
            metadata: Optional additional metadata
            config_override: Override default configuration

        Returns:
            Structured error response
        """
        ***REMOVED*** Merge configuration
        error_config = {
            **self._defaults["errors"],
            **(self.config.get("errors") or {}),
        }
        if config_override:
            error_config.update(config_override)

        error_info: dict[str, Any] = {
            "code": code,
            "message": message,
        }

        if details and error_config.get("include_details", True):
            error_info["details"] = details

        if suggestions and error_config.get("include_suggestions", True):
            error_info["suggestions"] = suggestions

        response: ErrorResponse = {
            "error": error_info,  ***REMOVED*** type: ignore
        }

        if metadata:
            response["metadata"] = metadata

        return response

    def success(
        self,
        data: Any,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a simple success response.

        Args:
            data: The response data
            message: Optional success message
            metadata: Optional additional metadata

        Returns:
            Simple success response
        """
        response = {"data": data}

        if message:
            response["message"] = message

        if metadata:
            response["metadata"] = metadata

        return response
