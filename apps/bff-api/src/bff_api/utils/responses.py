"""Response utilities for BFF API using fast-core patterns.

This module provides standardized response formats for BFF API endpoints
using fast-core response utilities for consistency across all routes.
"""

from typing import Any

from config.logging import get_logger
from fast_core.errors.responses import (
    create_paginated_response,
    create_success_response,
)

logger = get_logger(__name__)


def create_movie_list_response(
    movies: list[dict[str, Any]],
    total: int,
    page: int,
    per_page: int,
    message: str | None = None,
) -> dict[str, Any]:
    """Create standardized movie list response.

    Args:
        movies: List of movie data
        total: Total number of movies
        page: Current page number
        per_page: Items per page
        message: Optional success message

    Returns:
        Standardized paginated response
    """
    paginated_data = create_paginated_response(
        data=movies, page=page, page_size=per_page, total_items=total
    )

    # Add success message to the response
    if message:
        paginated_data["message"] = message

    return paginated_data


def create_movie_detail_response(
    movie: dict[str, Any],
    message: str | None = None,
) -> dict[str, Any]:
    """Create standardized movie detail response.

    Args:
        movie: Movie detail data
        message: Optional success message

    Returns:
        Standardized success response
    """
    return create_success_response(
        data=movie, message=message or "Movie details retrieved successfully"
    )


def create_search_response(
    results: list[dict[str, Any]],
    query: str,
    total: int,
    page: int,
    has_next: bool = False,
    message: str | None = None,
) -> dict[str, Any]:
    """Create standardized search response.

    Args:
        results: Search results
        query: Search query
        total: Total number of results
        page: Current page number
        has_next: Whether there are more results
        message: Optional success message

    Returns:
        Standardized search response
    """
    return create_success_response(
        data={
            "query": query,
            "results": results,
            "total_count": total,
            "page": page,
            "has_next": has_next,
        },
        message=message or f"Search completed for '{query}'",
    )


def create_home_screen_response(
    featured_movies: list[dict[str, Any]],
    popular_movies: list[dict[str, Any]],
    recent_releases: list[dict[str, Any]],
    user_recommendations: list[dict[str, Any]],
    genres: list[dict[str, Any]],
    message: str | None = None,
) -> dict[str, Any]:
    """Create standardized home screen response.

    Args:
        featured_movies: Featured movies list
        popular_movies: Popular movies list
        recent_releases: Recent releases list
        user_recommendations: User recommendations list
        genres: Available genres list
        message: Optional success message

    Returns:
        Standardized home screen response
    """
    return create_success_response(
        data={
            "featured_movies": featured_movies,
            "popular_movies": popular_movies,
            "recent_releases": recent_releases,
            "user_recommendations": user_recommendations,
            "genres": genres,
        },
        message=message or "Home screen data retrieved successfully",
    )


def create_suggestions_response(
    suggestions: list[dict[str, Any]],
    query: str,
    message: str | None = None,
) -> dict[str, Any]:
    """Create standardized suggestions response.

    Args:
        suggestions: List of suggestions
        query: Search query
        message: Optional success message

    Returns:
        Standardized suggestions response
    """
    return create_success_response(
        data={
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions),
        },
        message=message or f"Suggestions retrieved for '{query}'",
    )
