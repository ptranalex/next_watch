"""Movie models for the Recommendation API.

This module contains Pydantic models for movie data and vector representations,
including validation rules and data structures.
"""

from pydantic import BaseModel, ConfigDict, Field


class MovieMetadata(BaseModel):
    """Model for movie metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    original_title: str | None = Field(None, description="Original title")
    overview: str | None = Field(None, description="Movie overview/synopsis")
    release_date: str | None = Field(None, description="Release date")
    runtime: int | None = Field(None, description="Runtime in minutes")
    poster_path: str | None = Field(None, description="Poster image path")
    backdrop_path: str | None = Field(None, description="Backdrop image path")
    genres: list[str] = Field(default_factory=list, description="Movie genres")
    imdb_id: str | None = Field(None, description="IMDb ID")
    imdb_rating: float | None = Field(None, description="IMDb rating")
    vote_count: int | None = Field(None, description="Number of votes")
    popularity: float | None = Field(None, description="Popularity score")
    adult: bool = Field(False, description="Adult content flag")
    language: str | None = Field(None, description="Original language")


class MovieVector(BaseModel):
    """Model for movie vector representation."""

    model_config = ConfigDict(from_attributes=True)

    movie_id: int = Field(..., description="Movie ID")
    vector: list[float] = Field(..., description="Embedding vector")
    vector_type: str = Field(..., description="Type of vector (content/user)")
    model_version: str = Field(..., description="Model version used")
    created_at: str = Field(..., description="Vector creation timestamp")
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Additional vector metadata",
    )


class Movie(BaseModel):
    """Complete movie model combining metadata and vector data."""

    model_config = ConfigDict(from_attributes=True)

    metadata: MovieMetadata = Field(..., description="Movie metadata")
    content_vector: MovieVector | None = Field(None, description="Content-based vector")
    user_vector: MovieVector | None = Field(None, description="User preference vector")
    similar_movies: list[int] = Field(
        default_factory=list,
        description="List of similar movie IDs",
    )
    recommendation_score: float | None = Field(
        None,
        description="Overall recommendation score",
    )
