"""
Movie schemas for API responses using Pydantic.
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GenreInfo(BaseModel):
    """Basic genre information for inclusion in movie responses."""

    id: int
    name: str
    tmdb_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    """Base movie fields shared across schemas."""

    title: str
    overview: str | None = None
    release_date: date | None = None


class MovieCreate(MovieBase):
    """Schema for creating a new movie."""

    tmdb_id: int
    genre_ids: list[int] = []
    imdb_id: str | None = None
    original_title: str | None = None
    language: str | None = None
    original_language: str | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None


class MovieResponse(BaseModel):
    """Schema for movie responses including database ID."""

    id: int
    tmdb_id: int
    title: str
    overview: str | None = None
    release_date: date | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    vote_average: float | None = None
    popularity: float | None = None
    imdb_rating: float | None = None
    imdb_id: str | None = None
    runtime: int | None = None
    director: str | None = None
    writer: str | None = None
    genres: list[dict[str, Any]] = Field(default_factory=list)
    metacritic_rating: int | None = None
    rotten_tomatoes_rating: int | None = None
    awards: str | None = None
    original_language: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "MovieResponse":
        if isinstance(obj, dict):
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class MoviesListResponse(BaseModel):
    """Schema for paginated movie list responses."""

    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    results: list[MovieResponse]
