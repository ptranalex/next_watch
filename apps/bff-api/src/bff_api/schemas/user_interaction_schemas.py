"""User interaction schemas for BFF API."""

from pydantic import BaseModel, ConfigDict, Field


class UserMovieInteractionResponse(BaseModel):
    """Response model for user movie interactions."""

    user_id: int
    movie_id: int
    watched: bool = False
    liked: bool = False
    in_watchlist: bool = False
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class UserMovieInteractionUpdate(BaseModel):
    """Update model for user movie interactions."""

    watched: bool | None = None
    liked: bool | None = None
    in_watchlist: bool | None = None


class ToggleInteractionRequest(BaseModel):
    """Request model for toggling a specific interaction type."""

    interaction_type: str = Field(
        ...,
        description="Type of interaction to toggle",
        pattern="^(watched|liked|in_watchlist)$",
    )


class ToggleInteractionResponse(BaseModel):
    """Response model for toggle interaction endpoint."""

    success: bool
    message: str
    interaction: UserMovieInteractionResponse


# ============================================================================
# New Collection-Oriented Schemas
# ============================================================================


class AddToCollectionRequest(BaseModel):
    """Request model for adding a movie to a user collection (watchlist, liked, etc.)."""

    movie_id: int = Field(..., description="Movie ID to add to collection", ge=1)


class MovieCollectionItem(BaseModel):
    """Represents a movie in a user collection."""

    movie_id: int
    user_id: int
    added_at: str
    # Note: We could expand this later to include movie details if needed

    model_config = ConfigDict(from_attributes=True)


class MovieCollectionResponse(BaseModel):
    """Response model for movie collections (watchlist, liked movies, watched movies)."""

    items: list[MovieCollectionItem]
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class CollectionOperationResponse(BaseModel):
    """Response model for collection operations (add/remove)."""

    success: bool
    message: str
    movie_id: int
    collection_type: str  # "watchlist", "liked_movies", "watched_movies"
