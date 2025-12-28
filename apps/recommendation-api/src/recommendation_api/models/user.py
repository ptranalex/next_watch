"""User models for the Recommendation API.

This module contains Pydantic models for user preferences and profiles,
including validation rules and data structures.
"""

from pydantic import BaseModel, ConfigDict, Field


class UserPreferences(BaseModel):
    """Model for user preferences and settings."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(..., description="User ID")
    favorite_genres: list[str] = Field(default_factory=list, description="User's favorite genres")
    favorite_actors: list[str] = Field(default_factory=list, description="User's favorite actors")
    favorite_directors: list[str] = Field(
        default_factory=list, description="User's favorite directors"
    )
    min_rating: float = Field(6.0, ge=0.0, le=10.0, description="Minimum rating preference")
    preferred_years: list[int] | None = Field(None, description="Preferred release years")
    excluded_genres: list[str] = Field(default_factory=list, description="Genres to exclude")
    language_preference: str | None = Field(None, description="Preferred language")
    include_adult: bool = Field(False, description="Include adult content")


class UserProfile(BaseModel):
    """Model for user profile and recommendation context."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(..., description="User ID")
    preferences: UserPreferences = Field(..., description="User preferences")
    watch_history: list[int] = Field(default_factory=list, description="List of watched movie IDs")
    liked_movies: list[int] = Field(default_factory=list, description="List of liked movie IDs")
    watchlist: list[int] = Field(default_factory=list, description="List of watchlist movie IDs")
    last_watched: int | None = Field(None, description="Last watched movie ID")
    last_recommendation: str | None = Field(None, description="Timestamp of last recommendation")
    recommendation_count: int = Field(0, description="Number of recommendations generated")
    engagement_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="User engagement metrics (e.g., click-through rate)",
    )
