"""Recommendation models for the Recommendation API.

This module contains Pydantic models for recommendation requests and responses,
including validation rules and data structures.
"""

import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MovieRecommendation(BaseModel):
    """Model for a single movie recommendation."""

    id: int = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    overview: Optional[str] = Field(None, description="Movie overview/plot")
    release_date: Optional[date] = Field(None, description="Release date")
    imdb_rating: Optional[float] = Field(None, ge=0, le=10, description="IMDb rating (0-10)")
    tmdb_rating: Optional[float] = Field(None, ge=0, le=10, description="TMDB rating (0-10)")
    poster_url: Optional[str] = Field(None, description="URL to movie poster")
    genres: Optional[List[str]] = Field(None, description="List of genres")
    score: Optional[float] = Field(None, ge=0, le=1, description="Similarity score (0-1)")
    reason: Optional[str] = Field(None, description="Reason for recommendation")

    @classmethod
    def from_movie(
        cls, movie: Any, reason: Optional[str] = None, score: Optional[float] = None
    ) -> "MovieRecommendation":
        """Create a MovieRecommendation from a Movie model.

        Args:
            movie: Movie model instance
            reason: Reason for recommendation
            score: Similarity score

        Returns:
            MovieRecommendation instance
        """
        if not hasattr(movie, "id") or movie.id is None:
            raise ValueError("Movie must have a valid ID")

        ***REMOVED*** Handle different date formats
        release_date = None
        if hasattr(movie, "release_date") and movie.release_date:
            if isinstance(movie.release_date, (date, datetime)):
                release_date = movie.release_date
            elif isinstance(movie.release_date, str):
                try:
                    release_date = datetime.strptime(movie.release_date, "%Y-%m-%d").date()
                except ValueError:
                    pass

        ***REMOVED*** Handle genres - extract names from Genre objects if needed
        genres = None
        if hasattr(movie, "genres") and movie.genres:
            if isinstance(movie.genres, list):
                genres = [
                    genre.name if hasattr(genre, "name") else str(genre) for genre in movie.genres
                ]
            elif isinstance(movie.genres, str):
                genres = [movie.genres]

        return cls(
            id=movie.id,
            title=movie.title if hasattr(movie, "title") else "Unknown",
            overview=movie.overview if hasattr(movie, "overview") else None,
            release_date=release_date,
            imdb_rating=movie.imdb_rating if hasattr(movie, "imdb_rating") else None,
            tmdb_rating=movie.tmdb_rating if hasattr(movie, "tmdb_rating") else None,
            poster_url=movie.poster_path if hasattr(movie, "poster_path") else None,
            genres=genres,
            score=score,
            reason=reason,
        )


class RecommendationsResponse(BaseModel):
    """Response model for movie recommendations."""

    recommendations: List[MovieRecommendation] = Field(
        ..., description="List of movie recommendations"
    )
    total: int = Field(..., ge=0, description="Total number of recommendations")
    type: str = Field(..., description="Type of recommendations")
    filters: Dict[str, Any] = Field({}, description="Filters used for recommendations")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of response")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat(),
        }


class PersonalizedRecommendationsResponse(RecommendationsResponse):
    """Response model for personalized movie recommendations."""

    user_id: int = Field(..., description="User ID recommendations are for")


class SimilarMoviesResponse(RecommendationsResponse):
    """Response model for similar movie recommendations."""

    movie_id: int = Field(..., description="Source movie ID recommendations are based on")


class RecommendationRequest(BaseModel):
    """Model for recommendation request parameters."""

    user_id: int = Field(..., description="User ID to generate recommendations for")
    count: int = Field(10, ge=1, le=50, description="Number of recommendations to return")
    min_rating: float = Field(6.0, ge=0.0, le=10.0, description="Minimum IMDb rating")
    genres: Optional[List[str]] = Field(None, description="Filter by genres")
    exclude_watched: bool = Field(True, description="Exclude already watched movies")
    include_trending: bool = Field(True, description="Include trending movies")
    diversity_boost: bool = Field(True, description="Apply diversity boost")


class RecommendationResponse(BaseModel):
    """Model for recommendation response."""

    user_id: int = Field(..., description="User ID recommendations were generated for")
    recommendations: List[MovieRecommendation] = Field(
        ..., description="List of movie recommendations"
    )
    total_count: int = Field(..., description="Total number of recommendations")
    source: str = Field(..., description="Recommendation source (collaborative/content/hybrid)")
    timestamp: str = Field(..., description="Timestamp of recommendation generation")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
