"""
User movie interaction schemas for API responses using Pydantic.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class UserMovieInteractionBase(BaseModel):
    """Base model for user movie interactions."""

    movie_id: int
    watched: bool = False
    liked: bool = False
    in_watchlist: bool = False


class UserMovieInteractionCreate(UserMovieInteractionBase):
    """Create model for user movie interactions."""

    user_id: int


class UserMovieInteractionUpdate(BaseModel):
    """Schema for updating a user movie interaction."""

    watched: Optional[bool] = None
    liked: Optional[bool] = None
    in_watchlist: Optional[bool] = None


class UserMovieInteractionResponse(UserMovieInteractionBase):
    """Response model for user movie interactions."""

    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MovieSummary(BaseModel):
    """Summary of a movie for listing purposes."""

    id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[datetime] = None
    tmdb_rating: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class UserMovieInteractionWithMovie(BaseModel):
    """User movie interaction with movie details."""

    interaction: UserMovieInteractionResponse
    movie: MovieSummary

    model_config = ConfigDict(from_attributes=True)


class UserMovieDetail(BaseModel):
    """Detailed information about a movie with user interaction status."""

    interaction_id: Optional[int] = None
    movie_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    watched: bool = False
    liked: bool = False
    in_watchlist: bool = False
    imdb_rating: Optional[float] = None


class UserMovieInteractionsListResponse(BaseModel):
    """Schema for paginated user movie interaction list responses."""

    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    results: List[UserMovieInteractionResponse]


class UserMovieInteractionsWithMovieListResponse(BaseModel):
    """Schema for paginated user movie interaction with movie details list responses."""

    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    results: List[UserMovieInteractionWithMovie]


***REMOVED*** ============================================================================
***REMOVED*** NEW COLLECTION-ORIENTED SCHEMAS
***REMOVED*** ============================================================================


class AddToCollectionRequest(BaseModel):
    """Request model for adding a movie to a user collection."""

    movie_id: int = Field(..., description="Movie ID to add to collection", ge=1)


class CollectionItemResponse(BaseModel):
    """Response model for a single item in a user collection."""

    movie_id: int
    user_id: int
    added_at: datetime = Field(..., description="When the item was added to the collection")

    model_config = ConfigDict(from_attributes=True)


class CollectionResponse(BaseModel):
    """Response model for user collections (watchlist, watched movies, liked movies)."""

    items: List[CollectionItemResponse]
    total_count: int
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    has_next: bool = False
    has_prev: bool = False

    model_config = ConfigDict(from_attributes=True)


class CollectionOperationResponse(BaseModel):
    """Response model for collection operations (add/remove)."""

    success: bool
    message: str
    movie_id: int
    collection_type: str = Field(
        ..., description="Type of collection: watchlist, watched_movies, liked_movies"
    )
    operation: str = Field(..., description="Operation performed: added, removed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class CollectionStatsResponse(BaseModel):
    """Response model for collection statistics."""

    collection_type: str
    total_count: int
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserCollectionsSummaryResponse(BaseModel):
    """Response model for summary of all user collections."""

    watchlist: CollectionStatsResponse
    watched_movies: CollectionStatsResponse
    liked_movies: CollectionStatsResponse
    total_interactions: int

    model_config = ConfigDict(from_attributes=True)
