"""Response utilities for BFF API using fast-core patterns.

This module provides standardized response formats for BFF API endpoints
using fast-core response utilities for consistency across all routes.
"""

from typing import Any, Dict, List, Optional

from fast_core.errors.responses import create_success_response, create_paginated_response
from config.logging import get_logger

logger = get_logger(__name__)


def create_movie_list_response(
    movies: List[Dict[str, Any]],
    total: int,
    page: int,
    per_page: int,
    message: Optional[str] = None,
) -> Dict[str, Any]:
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

    ***REMOVED*** Add success message to the response
    if message:
        paginated_data["message"] = message

    return paginated_data


def create_movie_detail_response(
    movie: Dict[str, Any],
    message: Optional[str] = None,
) -> Dict[str, Any]:
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
    results: List[Dict[str, Any]],
    query: str,
    total: int,
    page: int,
    has_next: bool = False,
    message: Optional[str] = None,
) -> Dict[str, Any]:
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
    featured_movies: List[Dict[str, Any]],
    popular_movies: List[Dict[str, Any]],
    recent_releases: List[Dict[str, Any]],
    user_recommendations: List[Dict[str, Any]],
    genres: List[Dict[str, Any]],
    message: Optional[str] = None,
) -> Dict[str, Any]:
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
    suggestions: List[Dict[str, Any]],
    query: str,
    message: Optional[str] = None,
) -> Dict[str, Any]:
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
