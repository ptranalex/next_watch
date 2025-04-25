"""
Query utilities for the backend API.

This package contains specialized query implementations for business logic,
keeping it separate from the core data storage layer.
"""

from backend_api.queries.top_movies import get_top_rated_movies
from backend_api.queries.movie_details import (
    get_movie_details_by_id,
    get_movie_details_by_tmdb_id,
    get_movie_genres,
)
from backend_api.queries.movie_listings import (
    get_movies_with_filters,
    search_movies_by_title,
)
from backend_api.queries.genres import get_genre_by_name

***REMOVED*** Re-export all query functions for easier imports
__all__ = [
    "get_top_rated_movies",
    "get_movie_details_by_id",
    "get_movie_details_by_tmdb_id",
    "get_movie_genres",
    "get_movies_with_filters",
    "search_movies_by_title",
    "get_genre_by_name",
]
