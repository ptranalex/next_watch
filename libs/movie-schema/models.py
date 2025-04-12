from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

from .enums import ContentRating, MediaType


class Movie(BaseModel):
    """Movie schema shared across applications."""

    id: str = Field(..., description="Unique identifier for the movie")
    title: str = Field(..., description="Movie title")
    original_title: Optional[str] = Field(
        None, description="Original title in source language"
    )
    overview: Optional[str] = Field(None, description="Movie overview/description")
    release_date: Optional[date] = Field(None, description="Release date")
    poster_path: Optional[str] = Field(None, description="Path to poster image")
    backdrop_path: Optional[str] = Field(None, description="Path to backdrop image")
    popularity: float = Field(0.0, description="Popularity score")
    vote_average: float = Field(0.0, description="Average vote score")
    vote_count: int = Field(0, description="Number of votes")
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    genres: List[str] = Field(default_factory=list, description="List of genres")
    content_rating: Optional[ContentRating] = Field(None, description="Content rating")
    media_type: MediaType = Field(MediaType.MOVIE, description="Media type")

    class Config:
        frozen = True


class TVShow(BaseModel):
    """TV Show schema shared across applications."""

    id: str = Field(..., description="Unique identifier for the TV show")
    title: str = Field(..., description="TV show title")
    original_title: Optional[str] = Field(
        None, description="Original title in source language"
    )
    overview: Optional[str] = Field(None, description="TV show overview/description")
    first_air_date: Optional[date] = Field(None, description="First air date")
    poster_path: Optional[str] = Field(None, description="Path to poster image")
    backdrop_path: Optional[str] = Field(None, description="Path to backdrop image")
    popularity: float = Field(0.0, description="Popularity score")
    vote_average: float = Field(0.0, description="Average vote score")
    vote_count: int = Field(0, description="Number of votes")
    number_of_seasons: int = Field(0, description="Number of seasons")
    number_of_episodes: int = Field(0, description="Number of episodes")
    genres: List[str] = Field(default_factory=list, description="List of genres")
    content_rating: Optional[ContentRating] = Field(None, description="Content rating")
    media_type: MediaType = Field(MediaType.TV, description="Media type")

    class Config:
        frozen = True
