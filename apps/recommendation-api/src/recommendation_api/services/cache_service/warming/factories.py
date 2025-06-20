"""Recommendation API Cache Warming Target Factories.

This module provides factories to create warming targets for different strategies.
"""

from typing import Any, Dict, List, Optional

from cache.warming import WarmingTarget
from config.logging import get_logger

logger = get_logger(__name__)


class RecommendationTargetFactories:
    """Target factories for recommendation warming strategies."""

    def __init__(self) -> None:
        """Initialize the target factories."""
        pass

    def create_similar_movies_targets(
        self, movie_ids: List[int], limit: int = 20, min_score: float = 0.01
    ) -> List[WarmingTarget]:
        """Create warming targets for similar movies.

        Args:
            movie_ids: List of movie IDs to create targets for
            limit: Maximum number of similar movies to return
            min_score: Minimum similarity score threshold

        Returns:
            List of warming targets
        """
        targets = []
        for movie_id in movie_ids:
            targets.append(
                WarmingTarget(
                    function_name="similar_movies",
                    parameters={
                        "movie_id": movie_id,
                        "limit": limit,
                        "min_score": min_score,
                    },
                    priority=1.0,  ***REMOVED*** High priority for similar movies
                )
            )

        logger.info(f"Created {len(targets)} similar movies warming targets")
        return targets

    def create_popular_movies_targets(
        self, limits: List[int] = [10, 20, 50], min_ratings: List[float] = [7.0, 7.5]
    ) -> List[WarmingTarget]:
        """Create warming targets for popular movies with different parameters.

        Args:
            limits: List of limit values to create targets for
            min_ratings: List of minimum rating values to create targets for

        Returns:
            List of warming targets
        """
        targets = []

        ***REMOVED*** Create targets for different combinations of parameters
        for limit in limits:
            for min_rating in min_ratings:
                targets.append(
                    WarmingTarget(
                        function_name="popular_movies",
                        parameters={
                            "limit": limit,
                            "min_rating": min_rating,
                            "min_vote_count": 1000,
                        },
                        priority=0.8,  ***REMOVED*** Medium-high priority
                    )
                )

        logger.info(f"Created {len(targets)} popular movies warming targets")
        return targets

    def create_trending_movies_targets(
        self, limits: List[int] = [10, 20, 50], days_values: List[int] = [7, 30]
    ) -> List[WarmingTarget]:
        """Create warming targets for trending movies with different parameters.

        Args:
            limits: List of limit values to create targets for
            days_values: List of days values to create targets for

        Returns:
            List of warming targets
        """
        targets = []

        ***REMOVED*** Create targets for different combinations of parameters
        for limit in limits:
            for days in days_values:
                targets.append(
                    WarmingTarget(
                        function_name="trending_movies",
                        parameters={
                            "limit": limit,
                            "days": days,
                            "min_rating": None,
                        },
                        priority=0.7,  ***REMOVED*** Medium priority
                    )
                )

                ***REMOVED*** Also create targets with min_rating
                targets.append(
                    WarmingTarget(
                        function_name="trending_movies",
                        parameters={
                            "limit": limit,
                            "days": days,
                            "min_rating": 7.0,
                        },
                        priority=0.7,  ***REMOVED*** Medium priority
                    )
                )

        logger.info(f"Created {len(targets)} trending movies warming targets")
        return targets

    def create_popular_content_targets(
        self, popularity_data: Dict[str, Any]
    ) -> List[WarmingTarget]:
        """Create warming targets based on popularity data.

        Args:
            popularity_data: Dictionary containing popularity data

        Returns:
            List of warming targets
        """
        targets = []

        ***REMOVED*** Create similar movies targets for popular and trending movies
        popular_movie_ids = popularity_data.get("popular_movie_ids", [])
        if popular_movie_ids:
            ***REMOVED*** Take top 20 popular movies
            top_popular_ids = popular_movie_ids[:20]
            targets.extend(self.create_similar_movies_targets(top_popular_ids))

        trending_movie_ids = popularity_data.get("trending_movie_ids", [])
        if trending_movie_ids:
            ***REMOVED*** Take top 20 trending movies
            top_trending_ids = trending_movie_ids[:20]
            targets.extend(self.create_similar_movies_targets(top_trending_ids))

        recent_movie_ids = popularity_data.get("recent_movie_ids", [])
        if recent_movie_ids:
            ***REMOVED*** Take top 10 recent movies
            top_recent_ids = recent_movie_ids[:10]
            targets.extend(self.create_similar_movies_targets(top_recent_ids))

        ***REMOVED*** Add popular and trending movies targets
        targets.extend(self.create_popular_movies_targets())
        targets.extend(self.create_trending_movies_targets())

        logger.info(f"Created {len(targets)} total popular content warming targets")
        return targets
