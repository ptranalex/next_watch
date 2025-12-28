"""Data models and schemas for the Recommendation API.

This package contains Pydantic models for request/response validation
and SQLAlchemy models for database operations.
"""

from recommendation_api.models.movie import (
    Movie,
    MovieMetadata,
    MovieVector,
)
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    PersonalizedRecommendationsResponse,
    RecommendationsResponse,
    SimilarMoviesResponse,
)
from recommendation_api.models.user import (
    UserPreferences,
    UserProfile,
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
