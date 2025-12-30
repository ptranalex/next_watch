"""BFF Cache Warming Target Factories.

This module provides target factory implementations for creating warming targets
from popularity data for different content types (movies, actors, genres).
"""

from typing import Any

from cache.warming.types import WarmingStrategy, WarmingTarget
from config.logging import get_logger

logger = get_logger(__name__)


class BFFTargetFactories:
    """Target factories for creating warming targets from BFF content data."""

    def __init__(self) -> None:
        """Initialize the target factories."""
        pass

    def create_movie_targets(self, movie_item: dict[str, Any]) -> list[WarmingTarget]:
        """Create warming targets for a popular movie item.

        Args:
            movie_item: Movie popularity data with id, popularity_score, view_count

        Returns:
            List of warming targets for this movie
        """
        targets: list[WarmingTarget] = []
        movie_id = movie_item.get("id")
        popularity_score = movie_item.get("popularity_score", 1.0)
        view_count = movie_item.get("view_count", 0)

        if not movie_id:
            return targets

        # Calculate base priority
        base_priority = self._calculate_priority_for_item(popularity_score, view_count, "movie")

        # Movie detail screen for anonymous users
        # This is the most valuable warming target since:
        # 1. It can be shared across all anonymous users
        # 2. It has long TTL (30 minutes vs 30 minutes for authenticated)
        # 3. No user-specific data means no credentials needed during warming
        # 4. Covers the majority of traffic (anonymous browsing)
        targets.append(
            WarmingTarget(
                function_name="movie_screen",
                parameters={"movie_id": movie_id, "user_id": None},
                priority=base_priority,
                estimated_benefit=popularity_score * 100,
                strategy=WarmingStrategy.POPULAR_CONTENT,
            )
        )

        # Note: We don't warm user-specific versions because:
        # - Warming has no JWT credentials, so user interaction data defaults to False anyway
        # - User-specific caches are short-lived and personalized
        # - Better to warm them on-demand when users actually visit
        # - Anonymous cache covers the majority of use cases

        return targets

    def create_actor_targets(self, actor_item: dict[str, Any]) -> list[WarmingTarget]:
        """Create warming targets for a popular actor item.

        Args:
            actor_item: Actor popularity data with id, popularity_score, view_count

        Returns:
            List of warming targets for this actor
        """
        targets: list[WarmingTarget] = []
        actor_id = actor_item.get("id")
        popularity_score = actor_item.get("popularity_score", 1.0)
        view_count = actor_item.get("view_count", 0)

        if not actor_id:
            return targets

        # Calculate base priority
        base_priority = self._calculate_priority_for_item(popularity_score, view_count, "actor")

        # Actor profile screen
        targets.append(
            WarmingTarget(
                function_name="actor_screen",
                parameters={"actor_id": actor_id, "page": 1, "limit": 20},
                priority=base_priority * 0.9,
                estimated_benefit=popularity_score * 90,
                strategy=WarmingStrategy.POPULAR_CONTENT,
            )
        )

        return targets

    def create_genre_targets(self, genre_item: dict[str, Any]) -> list[WarmingTarget]:
        """Create warming targets for a popular genre item.

        Args:
            genre_item: Genre popularity data with id, popularity_score, view_count

        Returns:
            List of warming targets for this genre
        """
        targets: list[WarmingTarget] = []
        genre_id = genre_item.get("id")
        popularity_score = genre_item.get("popularity_score", 1.0)
        view_count = genre_item.get("view_count", 0)

        if not genre_id:
            return targets

        # Calculate base priority
        base_priority = self._calculate_priority_for_item(popularity_score, view_count, "genre")

        # Genre screen with default sorting
        targets.append(
            WarmingTarget(
                function_name="genre_screen",
                parameters={"genre_id": genre_id, "sort_by": "imdb_rating", "page": 1},
                priority=base_priority * 0.9,
                estimated_benefit=popularity_score * 90,
                strategy=WarmingStrategy.POPULAR_CONTENT,
            )
        )

        return targets

    def _calculate_priority_for_item(
        self, popularity_score: float, view_count: int, content_type: str
    ) -> float:
        """Calculate priority for a popularity item.

        Args:
            popularity_score: Popularity score
            view_count: View count
            content_type: Type of content

        Returns:
            Priority score
        """
        # Base priority from popularity
        base_priority = popularity_score

        # Boost based on view count (logarithmic scale)
        import math

        view_boost = math.log10(max(view_count, 1)) / 10.0

        # Content type multipliers
        type_multipliers = {"movie": 1.0, "actor": 0.8, "genre": 0.6}
        type_multiplier = type_multipliers.get(content_type, 0.3)

        return (base_priority + view_boost) * type_multiplier
