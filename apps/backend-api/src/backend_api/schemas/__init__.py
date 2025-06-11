"""
Schema module for the backend API.

This module provides Pydantic models for request and response validation.
"""

from .cast_schema import CastMemberResponse, MovieCastResponse
from .genre_schema import GenreResponse
from .movie_schema import MovieResponse, MoviesListResponse
from .search import SearchResponse, SearchResult
from .trailer_schema import TrailerResponse
from .user_interaction_schema import (
    MovieSummary,
    UserMovieDetail,
    UserMovieInteractionResponse,
    UserMovieInteractionWithMovie,
)

__all__ = [
    "CastMemberResponse",
    "MovieCastResponse",
    "GenreResponse",
    "MovieResponse",
    "MoviesListResponse",
    "SearchResponse",
    "SearchResult",
    "TrailerResponse",
    "MovieSummary",
    "UserMovieDetail",
    "UserMovieInteractionResponse",
    "UserMovieInteractionWithMovie",
]
