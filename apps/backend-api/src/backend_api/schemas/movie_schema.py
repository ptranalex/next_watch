"""
Movie schemas for API responses using Pydantic.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime


class GenreInfo(BaseModel):
    """Basic genre information for inclusion in movie responses."""

    id: int
    name: str
    tmdb_id: Optional[int] = None

    class Config:
        orm_mode = True


class MovieBase(BaseModel):
    """Base movie fields shared across schemas."""

    title: str
    overview: Optional[str] = None
    release_date: Optional[date] = None


class MovieCreate(MovieBase):
    """Schema for creating a new movie."""

    tmdb_id: int
    genre_ids: List[int] = []
    imdb_id: Optional[str] = None
    original_title: Optional[str] = None
    language: Optional[str] = None
    original_language: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None


class MovieResponse(BaseModel):
    """Schema for movie responses including database ID."""

    id: int
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[date] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    vote_average: Optional[float] = None
    imdb_rating: Optional[float] = None
    imdb_id: Optional[str] = None
    runtime: Optional[int] = None
    director: Optional[str] = None
    genres: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        extra = "ignore"

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict):
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class MoviesListResponse(BaseModel):
    """Schema for paginated movie list responses."""

    movies: List[MovieResponse]
    total: int
    page: int
    page_size: int
