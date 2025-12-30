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
    AddToCollectionRequest,
    CollectionItemResponse,
    CollectionOperationResponse,
    CollectionResponse,
    CollectionStatsResponse,
    MovieSummary,
    UserCollectionsSummaryResponse,
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
    # User interaction schemas
    "MovieSummary",
    "UserMovieDetail",
    "UserMovieInteractionResponse",
    "UserMovieInteractionWithMovie",
    # New collection-oriented schemas
    "AddToCollectionRequest",
    "CollectionItemResponse",
    "CollectionOperationResponse",
    "CollectionResponse",
    "CollectionStatsResponse",
    "UserCollectionsSummaryResponse",
]
