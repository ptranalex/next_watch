"""Movie models for the Recommendation API.

This module contains Pydantic models for movie data and vector representations,
including validation rules and data structures.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class MovieMetadata(BaseModel):
    """Model for movie metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    original_title: Optional[str] = Field(None, description="Original title")
    overview: Optional[str] = Field(None, description="Movie overview/synopsis")
    release_date: Optional[str] = Field(None, description="Release date")
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    poster_path: Optional[str] = Field(None, description="Poster image path")
    backdrop_path: Optional[str] = Field(None, description="Backdrop image path")
    genres: List[str] = Field(default_factory=list, description="Movie genres")
    imdb_id: Optional[str] = Field(None, description="IMDb ID")
    imdb_rating: Optional[float] = Field(None, description="IMDb rating")
    vote_count: Optional[int] = Field(None, description="Number of votes")
    popularity: Optional[float] = Field(None, description="Popularity score")
    adult: bool = Field(False, description="Adult content flag")
    language: Optional[str] = Field(None, description="Original language")


class MovieVector(BaseModel):
    """Model for movie vector representation."""

    model_config = ConfigDict(from_attributes=True)

    movie_id: int = Field(..., description="Movie ID")
    vector: List[float] = Field(..., description="Embedding vector")
    vector_type: str = Field(..., description="Type of vector (content/user)")
    model_version: str = Field(..., description="Model version used")
    created_at: str = Field(..., description="Vector creation timestamp")
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional vector metadata",
    )


class Movie(BaseModel):
    """Complete movie model combining metadata and vector data."""

    model_config = ConfigDict(from_attributes=True)

    metadata: MovieMetadata = Field(..., description="Movie metadata")
    content_vector: Optional[MovieVector] = Field(None, description="Content-based vector")
    user_vector: Optional[MovieVector] = Field(None, description="User preference vector")
    similar_movies: List[int] = Field(
        default_factory=list,
        description="List of similar movie IDs",
    )
    recommendation_score: Optional[float] = Field(
        None,
        description="Overall recommendation score",
    ) 