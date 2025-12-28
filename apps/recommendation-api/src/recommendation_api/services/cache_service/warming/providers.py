"""Recommendation API Cache Warming Data Providers.

This module provides data sources for various warming strategies including
popularity data and trending movie data.
"""

from datetime import datetime
from typing import Any

from config.logging import get_logger

from recommendation_api.config import settings
from recommendation_api.services.movie_adapter import get_movie_adapter

logger = get_logger(__name__)


class RecommendationDataProviders:
    """Data providers for recommendation warming strategies."""

    def __init__(self) -> None:
        """Initialize the data providers."""
        self.settings = settings
        self._movie_adapter = None

    @property
    def movie_adapter(self) -> Any:
        """Get or create the movie adapter."""
        if self._movie_adapter is None:
            self._movie_adapter = get_movie_adapter()
        return self._movie_adapter

    async def get_popularity_data(self) -> dict[str, Any]:
        """Get recommendation-specific popularity data for warming.

        Returns:
            Dictionary containing popular and trending movies
        """
        try:
            ***REMOVED*** Get popular movies - use max 50 per request to comply with backend API limits
            popular_movie_ids = await self._get_popular_movie_ids(limit=50)

            ***REMOVED*** Get trending movies
            trending_movie_ids = await self._get_trending_movie_ids(limit=50)

            ***REMOVED*** Get recently updated movies (for similar movies warming)
            recent_movie_ids = await self._get_recently_updated_movie_ids(limit=50)

            return {
                "popular_movie_ids": popular_movie_ids,
                "trending_movie_ids": trending_movie_ids,
                "recent_movie_ids": recent_movie_ids,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get popularity data: {e}")
            return {
                "popular_movie_ids": [],
                "trending_movie_ids": [],
                "recent_movie_ids": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _get_popular_movie_ids(self, limit: int = 50) -> list[int]:
        """Get popular movie IDs for warming.

        Args:
            limit: Maximum number of movie IDs to return (max 50)

        Returns:
            List of popular movie IDs
        """
        try:
            ***REMOVED*** Ensure limit doesn't exceed backend API maximum
            safe_limit = min(limit, 50)

            ***REMOVED*** Get popular movies from movie adapter
            popular_movies, _ = await self.movie_adapter.get_popular_movies(
                limit=safe_limit, min_rating=7.0, min_vote_count=1000
            )
            return [movie.id for movie in popular_movies if movie.id]
        except Exception as e:
            logger.error(f"Failed to get popular movie IDs: {e}")
            return []

    async def _get_trending_movie_ids(self, limit: int = 50) -> list[int]:
        """Get trending movie IDs for warming.

        Args:
            limit: Maximum number of movie IDs to return (max 50)

        Returns:
            List of trending movie IDs
        """
        try:
            ***REMOVED*** Ensure limit doesn't exceed backend API maximum
            safe_limit = min(limit, 50)

            ***REMOVED*** Get trending movies from movie adapter
            trending_movies, _ = await self.movie_adapter.get_trending_movies(
                limit=safe_limit, days=7
            )
            return [movie.id for movie in trending_movies if movie.id]
        except Exception as e:
            logger.error(f"Failed to get trending movie IDs: {e}")
            return []

    async def _get_recently_updated_movie_ids(self, limit: int = 50) -> list[int]:
        """Get recently updated movie IDs for warming similar movies.

        Args:
            limit: Maximum number of movie IDs to return (max 50)

        Returns:
            List of recently updated movie IDs
        """
        try:
            ***REMOVED*** Ensure limit doesn't exceed backend API maximum
            safe_limit = min(limit, 50)

            ***REMOVED*** Get recently updated movies from movie adapter
            recent_movies, _ = await self.movie_adapter.get_recent_movies(limit=safe_limit)
            return [movie.id for movie in recent_movies if movie.id]
        except Exception as e:
            logger.error(f"Failed to get recently updated movie IDs: {e}")
            return []
