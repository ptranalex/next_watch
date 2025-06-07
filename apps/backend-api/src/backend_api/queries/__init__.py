from typing import Any

"""
Queries module for the backend API.

This module provides database query utilities following CQRS principles.
"""

from .movie_query import MovieQuery
from .user_interaction_query import UserInteractionQuery

***REMOVED*** Import individual query modules
try:
    from backend_api.queries.top_movies import get_top_rated_movies
except ImportError:
    ***REMOVED*** Fallback for tests
    pass

try:
    from backend_api.queries.movie_details import (
        get_movie_details_by_id,
        get_movie_details_by_tmdb_id,
        get_movie_genres,
    )
except ImportError:
    ***REMOVED*** Fallback for tests
    pass

try:
    from backend_api.queries.movie_listings import get_movies_with_filters
except ImportError:
    ***REMOVED*** Fallback for tests
    pass

try:
    from backend_api.queries.trailer import get_trailers_for_movie
except ImportError:
    ***REMOVED*** Fallback for tests
    pass

__all__ = [
    "MovieQuery",
    "UserInteractionQuery",
    ***REMOVED*** Legacy functions
    "get_top_rated_movies",
    "get_movie_genres",
    "get_movies_with_filters",
    "get_movie_details_by_id",
    "get_movie_details_by_tmdb_id",
    "get_trailers_for_movie",
]
