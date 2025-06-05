"""Data models for embedding requests and responses."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MovieEmbeddingRequest(BaseModel):
    """Request model for generating a movie embedding."""

    movie_id: str = Field(..., description="Unique identifier for the movie")
    title: str = Field(..., description="Movie title")
    overview: str = Field(..., description="Movie overview/description")
    genres: List[str] = Field(default_factory=list, description="List of movie genres")
    additional_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional movie metadata"
    )


class MovieEmbeddingResponse(BaseModel):
    """Response model for a movie embedding."""

    movie_id: str = Field(..., description="Unique identifier for the movie")
    embedding: List[float] = Field(..., description="Vector representation of the movie")
    model_id: str = Field(..., description="Identifier of the model used for embedding")
    dimensions: int = Field(..., description="Dimensionality of the embedding vector")


class UserMovieRating(BaseModel):
    """Model for a user's movie rating."""

    movie_id: str = Field(..., description="Unique identifier for the movie")
    rating: float = Field(..., description="User rating for the movie")


class UserEmbeddingRequest(BaseModel):
    """Request model for generating a user preference vector."""

    user_id: str = Field(..., description="Unique identifier for the user")
    liked_movies: List[UserMovieRating] = Field(
        default_factory=list, description="Movies liked by the user with ratings"
    )
    watched_genres: Dict[str, float] = Field(
        default_factory=dict, description="Genres watched by the user with preference weights"
    )


class UserEmbeddingResponse(BaseModel):
    """Response model for a user preference vector."""

    user_id: str = Field(..., description="Unique identifier for the user")
    preference_vector: List[float] = Field(
        ..., description="Vector representation of user preferences"
    )
    model_id: str = Field(..., description="Identifier of the model used for embedding")
    dimensions: int = Field(..., description="Dimensionality of the embedding vector")


class ModelInfo(BaseModel):
    """Model for information about the embedding model."""

    model_id: str = Field(..., description="Identifier of the embedding model")
    dimensions: int = Field(..., description="Dimensionality of the embedding vectors")
    version: str = Field(..., description="Version of the model")
    status: str = Field(..., description="Current status of the model")
    health: str = Field(..., description="Health status of the model")
    stats: Dict[str, Union[int, float]] = Field(
        default_factory=dict, description="Statistics about model usage"
    )
