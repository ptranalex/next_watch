"""
Queries module for the backend API.

This module provides database query utilities following CQRS principles.
"""

from .movie_details import (
    get_movie_details_by_id,
    get_movie_details_by_tmdb_id,
    get_movie_genres,
)
from .movie_listings import get_movies_with_filters
from .movie_query import MovieQuery
from .top_movies import get_top_rated_movies
from .trailer import get_trailers_for_movie
from .user_interaction_query import UserInteractionQuery

__all__ = [
    "MovieQuery",
    "UserInteractionQuery",
    # Legacy functions
    "get_top_rated_movies",
    "get_movie_genres",
    "get_movies_with_filters",
    "get_movie_details_by_id",
    "get_movie_details_by_tmdb_id",
    "get_trailers_for_movie",
]
