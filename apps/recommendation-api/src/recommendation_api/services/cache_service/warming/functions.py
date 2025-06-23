"""Recommendation API Cache Warming Functions.

This module provides warming functions that call the actual cached endpoints
to populate the cache with recommendation data.
"""

from config.logging import get_logger
from typing import Any, Dict, List, Optional

from recommendation_api.config import settings
from recommendation_api.services.movie_adapter import MovieDataAdapter, get_movie_adapter
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.services.vector_service import get_vector_service

logger = get_logger(__name__)


class RecommendationWarmingFunctions:
    """Warming functions for recommendation API endpoints."""

    def __init__(self) -> None:
        """Initialize the warming functions."""
        self.settings = settings
        self._movie_adapter = None
        self._recommendation_service = None

    @property
    def movie_adapter(self) -> MovieDataAdapter:
        """Get or create the movie adapter.

        Returns:
            MovieDataAdapter instance
        """
        if self._movie_adapter is None:
            self._movie_adapter = get_movie_adapter()
        return self._movie_adapter

    @property
    def recommendation_service(self) -> RecommendationService:
        """Get or create the recommendation service.

        Creates a RecommendationService with proper dependencies using the factory pattern.

        Returns:
            RecommendationService instance
        """
        if self._recommendation_service is None:
            ***REMOVED*** Use factory pattern to create service with proper dependencies
            vector_service = get_vector_service()
            self._recommendation_service = RecommendationService(
                movie_adapter=self.movie_adapter,
                vector_service=vector_service,
            )
        return self._recommendation_service

    async def warm_similar_movies(
        self, movie_id: int, limit: int = 20, min_score: float = 0.01
    ) -> Dict[str, Any]:
        """Warm the similar movies cache for a specific movie.

        Args:
            movie_id: Movie ID to get similar movies for
            limit: Maximum number of similar movies to return
            min_score: Minimum similarity score threshold

        Returns:
            Dictionary with warming result metadata
        """
        try:
            ***REMOVED*** Import the actual cached function
            from recommendation_api.routes.v1.similar import _get_similar_movies_data

            ***REMOVED*** Call the cached function directly - this populates the cache
            similar_movies_data = await _get_similar_movies_data(
                movie_id=movie_id,
                limit=limit,
                min_score=min_score,
                recommendation_service=self.recommendation_service,
            )

            return {
                "cache_populated": True,
                "warming_type": "similar_movies",
                "movie_id": movie_id,
                "limit": limit,
                "min_score": min_score,
                "results_count": similar_movies_data["total"],
            }

        except Exception as e:
            logger.error(f"Failed to warm similar movies for movie_id={movie_id}: {e}")
            return {
                "cache_populated": False,
                "warming_type": "similar_movies",
                "movie_id": movie_id,
                "error": str(e),
            }

    async def warm_popular_movies(
        self, limit: int = 20, min_rating: float = 7.0, min_vote_count: int = 1000
    ) -> Dict[str, Any]:
        """Warm the popular movies cache.

        Args:
            limit: Maximum number of popular movies to return
            min_rating: Minimum rating threshold
            min_vote_count: Minimum vote count threshold

        Returns:
            Dictionary with warming result metadata
        """
        try:
            ***REMOVED*** Import the actual cached function
            from recommendation_api.routes.v1.popular import _get_popular_recommendations_data

            ***REMOVED*** Call the cached function directly - this populates the cache
            popular_movies_data = await _get_popular_recommendations_data(
                limit=limit,
                min_rating=min_rating,
                min_vote_count=min_vote_count,
                recommendation_service=self.recommendation_service,
            )

            return {
                "cache_populated": True,
                "warming_type": "popular_movies",
                "limit": limit,
                "min_rating": min_rating,
                "min_vote_count": min_vote_count,
                "results_count": popular_movies_data["total"],
            }

        except Exception as e:
            logger.error(f"Failed to warm popular movies: {e}")
            return {
                "cache_populated": False,
                "warming_type": "popular_movies",
                "error": str(e),
            }

    async def warm_trending_movies(
        self, limit: int = 20, days: int = 7, min_rating: Optional[float] = None
    ) -> Dict[str, Any]:
        """Warm the trending movies cache.

        Args:
            limit: Maximum number of trending movies to return
            days: Number of days to consider for trending calculation
            min_rating: Optional minimum rating threshold

        Returns:
            Dictionary with warming result metadata
        """
        try:
            ***REMOVED*** Import the actual cached function
            from recommendation_api.routes.v1.trending import _get_trending_recommendations_data

            ***REMOVED*** Call the cached function directly - this populates the cache
            trending_movies_data = await _get_trending_recommendations_data(
                limit=limit,
                days=days,
                min_rating=min_rating,
                recommendation_service=self.recommendation_service,
            )

            return {
                "cache_populated": True,
                "warming_type": "trending_movies",
                "limit": limit,
                "days": days,
                "min_rating": min_rating,
                "results_count": trending_movies_data["total"],
            }

        except Exception as e:
            logger.error(f"Failed to warm trending movies: {e}")
            return {
                "cache_populated": False,
                "warming_type": "trending_movies",
                "error": str(e),
            }
