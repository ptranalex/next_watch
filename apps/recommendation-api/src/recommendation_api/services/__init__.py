"""Service layer for the Recommendation API.

This package contains service classes that implement the core business logic
for generating movie recommendations and managing user preferences.
"""

from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.services.vector_service import VectorService, get_vector_service

__all__ = [
    "RecommendationService",
    "VectorService",
    "get_vector_service",
] 