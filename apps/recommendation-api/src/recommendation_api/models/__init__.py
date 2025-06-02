"""Data models and schemas for the Recommendation API.

This package contains Pydantic models for request/response validation
and SQLAlchemy models for database operations.
"""

from recommendation_api.models.recommendation import (
    MovieRecommendation,
    RecommendationsResponse,
    PersonalizedRecommendationsResponse,
    SimilarMoviesResponse,
)
from recommendation_api.models.user import (
    UserPreferences,
    UserProfile,
)
from recommendation_api.models.movie import (
    Movie,
    MovieMetadata,
    MovieVector,
)

__all__ = [
    "MovieRecommendation",
    "RecommendationsResponse",
    "PersonalizedRecommendationsResponse",
    "SimilarMoviesResponse",
    "UserPreferences",
    "UserProfile",
    "Movie",
    "MovieMetadata",
    "MovieVector",
] 