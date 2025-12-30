"""User-specific warming strategy."""

from collections.abc import Awaitable, Callable
from typing import Any

import structlog

from cache.warming.types import WarmingConfig, WarmingStrategy, WarmingTarget

from .base import BaseWarmingStrategy

logger = structlog.get_logger(__name__)


class UserSpecificStrategy(BaseWarmingStrategy):
    """Warming strategy based on user preferences and behavior."""

    def __init__(
        self,
        config: WarmingConfig,
        user_data_provider: Callable[[int], Awaitable[dict[str, Any]]] | None = None,
        recommendation_provider: Callable[[int], Awaitable[list[dict[str, Any]]]] | None = None,
    ):
        """Initialize user-specific strategy.

        Args:
            config: Warming configuration
            user_data_provider: Function that returns user profile data
            recommendation_provider: Function that returns user recommendations
        """
        super().__init__(config)
        self.strategy_type = WarmingStrategy.USER_SPECIFIC
        self.user_data_provider = user_data_provider
        self.recommendation_provider = recommendation_provider

    async def identify_targets(
        self, limit: int | None = None, context: dict[str, Any] | None = None
    ) -> list[WarmingTarget]:
        """Identify warming targets based on user behavior and preferences.

        Args:
            limit: Maximum number of targets to return
            context: Context with user_ids or user segments

        Returns:
            List of warming targets for user-specific content
        """
        if not context or "user_ids" not in context:
            logger.warning("No user context provided for user-specific warming")
            return await self._get_default_user_targets(limit)

        user_ids = context.get("user_ids", [])
        if not user_ids:
            return await self._get_default_user_targets(limit)

        all_targets = []

        # Process each user
        for user_id in user_ids:
            try:
                user_targets = await self._process_user(user_id, limit)
                all_targets.extend(user_targets)
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                continue

        # Sort by priority and apply global limit
        all_targets.sort(key=lambda t: t.priority, reverse=True)
        if limit:
            all_targets = all_targets[:limit]

        logger.info(f"Identified {len(all_targets)} user-specific targets for warming")
        return all_targets

    async def _process_user(self, user_id: int, limit: int | None = None) -> list[WarmingTarget]:
        """Process warming targets for a specific user.

        Args:
            user_id: User ID to process
            limit: Maximum targets per user

        Returns:
            List of warming targets for the user
        """
        targets = []

        # Get user profile data
        user_data = {}
        if self.user_data_provider:
            try:
                user_data = await self.user_data_provider(user_id)
            except Exception as e:
                logger.error(f"Error getting user data for {user_id}: {e}")

        # Get user recommendations
        recommendations = []
        if self.recommendation_provider:
            try:
                recommendations = await self.recommendation_provider(user_id)
            except Exception as e:
                logger.error(f"Error getting recommendations for {user_id}: {e}")

        # Create targets based on user profile
        targets.extend(self._create_profile_targets(user_id, user_data))

        # Create targets based on recommendations
        targets.extend(self._create_recommendation_targets(user_id, recommendations, user_data))

        # Create targets based on user preferences
        targets.extend(self._create_preference_targets(user_id, user_data))

        # Sort and limit per user
        targets.sort(key=lambda t: t.priority, reverse=True)
        if limit:
            targets = targets[:limit]

        return targets

    def _create_profile_targets(
        self, user_id: int, user_data: dict[str, Any]
    ) -> list[WarmingTarget]:
        """Create warming targets based on user profile.

        Args:
            user_id: User ID
            user_data: User profile data

        Returns:
            List of warming targets
        """
        targets = []

        # User's watchlist
        watchlist = user_data.get("watchlist", [])
        for movie_id in watchlist[:10]:  # Top 10 watchlist items
            priority = self.calculate_priority(
                {
                    "user_engagement": "high",
                    "content_type": "watchlist",
                    "user_id": user_id,
                }
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_movie_screen_data",
                    parameters={"movie_id": movie_id, "user_id": user_id},
                    priority=priority,
                    estimated_benefit=150.0,  # High benefit for watchlist items
                )
            )

        # User's favorite genres
        favorite_genres = user_data.get("favorite_genres", [])
        for genre_id in favorite_genres[:5]:
            priority = self.calculate_priority(
                {
                    "user_engagement": "medium",
                    "content_type": "favorite_genre",
                    "user_id": user_id,
                }
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_genre_screen_data",
                    parameters={"genre_id": genre_id, "user_id": user_id, "page": 1},
                    priority=priority,
                    estimated_benefit=100.0,
                )
            )

        # User's recently viewed
        recently_viewed = user_data.get("recently_viewed", [])
        for movie_id in recently_viewed[:5]:
            priority = self.calculate_priority(
                {
                    "user_engagement": "medium",
                    "content_type": "recently_viewed",
                    "user_id": user_id,
                }
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_movie_screen_data",
                    parameters={"movie_id": movie_id, "user_id": user_id},
                    priority=priority * 0.8,  # Slightly lower priority
                    estimated_benefit=80.0,
                )
            )

        return targets

    def _create_recommendation_targets(
        self,
        user_id: int,
        recommendations: list[dict[str, Any]],
        user_data: dict[str, Any],
    ) -> list[WarmingTarget]:
        """Create warming targets based on user recommendations.

        Args:
            user_id: User ID
            recommendations: List of recommended items
            user_data: User profile data

        Returns:
            List of warming targets
        """
        targets = []

        for rec in recommendations[:15]:  # Top 15 recommendations
            movie_id = rec.get("movie_id")
            confidence = rec.get("confidence", 0.5)
            rec_type = rec.get("type", "general")

            if not movie_id:
                continue

            priority = self.calculate_priority(
                {
                    "user_engagement": "high" if confidence > 0.8 else "medium",
                    "content_type": f"recommendation_{rec_type}",
                    "confidence": confidence,
                    "user_id": user_id,
                }
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_movie_screen_data",
                    parameters={"movie_id": movie_id, "user_id": user_id},
                    priority=priority,
                    estimated_benefit=confidence * 120.0,
                )
            )

        return targets

    def _create_preference_targets(
        self, user_id: int, user_data: dict[str, Any]
    ) -> list[WarmingTarget]:
        """Create warming targets based on user preferences.

        Args:
            user_id: User ID
            user_data: User profile data

        Returns:
            List of warming targets
        """
        targets = []

        # User's preferred actors
        favorite_actors = user_data.get("favorite_actors", [])
        for actor_id in favorite_actors[:5]:
            priority = self.calculate_priority(
                {
                    "user_engagement": "medium",
                    "content_type": "favorite_actor",
                    "user_id": user_id,
                }
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_actor_screen_data",
                    parameters={"actor_id": actor_id, "user_id": user_id},
                    priority=priority,
                    estimated_benefit=90.0,
                )
            )

        # User's preferred time periods
        preferred_decades = user_data.get("preferred_decades", [])
        for decade in preferred_decades[:3]:
            priority = self.calculate_priority(
                {
                    "user_engagement": "low",
                    "content_type": "preferred_decade",
                    "user_id": user_id,
                }
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_movies_by_decade",
                    parameters={"decade": decade, "user_id": user_id, "page": 1},
                    priority=priority,
                    estimated_benefit=60.0,
                )
            )

        # User dashboard/profile screens
        priority = self.calculate_priority(
            {
                "user_engagement": "high",
                "content_type": "user_dashboard",
                "user_id": user_id,
            }
        )

        targets.append(
            self.create_warming_target(
                function_name="get_user_dashboard_data",
                parameters={"user_id": user_id},
                priority=priority,
                estimated_benefit=200.0,  # High benefit for personal dashboard
            )
        )

        return targets

    def calculate_priority(self, target_data: dict[str, Any]) -> float:
        """Calculate priority based on user engagement and content type.

        Args:
            target_data: User-specific target data

        Returns:
            Priority score
        """
        engagement_level = target_data.get("user_engagement", "low")
        content_type = target_data.get("content_type", "unknown")
        confidence = target_data.get("confidence", 0.5)

        # Base priority from engagement level
        engagement_multipliers = {"high": 3.0, "medium": 2.0, "low": 1.0}

        base_priority = engagement_multipliers.get(engagement_level, 1.0)

        # Content type multipliers
        content_multipliers = {
            "watchlist": 1.5,
            "user_dashboard": 1.4,
            "recommendation_collaborative": 1.3,
            "recommendation_content": 1.2,
            "favorite_genre": 1.1,
            "favorite_actor": 1.0,
            "recently_viewed": 0.9,
            "preferred_decade": 0.7,
            "unknown": 0.5,
        }

        content_multiplier = content_multipliers.get(content_type, 0.5)

        # Confidence boost for recommendations
        confidence_boost = confidence if "recommendation" in content_type else 1.0

        return (
            base_priority * content_multiplier * confidence_boost * self.config.user_specific_weight
        )

    async def _get_default_user_targets(self, limit: int | None = None) -> list[WarmingTarget]:
        """Get default user-specific targets when no user data is available.

        Args:
            limit: Maximum number of targets

        Returns:
            List of default warming targets
        """
        targets = []

        # Common user screens that are frequently accessed
        common_screens = [
            ("get_user_dashboard_data", {"user_id": None}, 4.0),
            ("get_watchlist_data", {"user_id": None}, 3.5),
            ("get_user_recommendations", {"user_id": None}, 3.0),
            ("get_user_profile_data", {"user_id": None}, 2.5),
        ]

        for func_name, params, priority in common_screens:
            targets.append(
                self.create_warming_target(
                    function_name=func_name,
                    parameters=params,
                    priority=priority,
                    estimated_benefit=priority * 20.0,
                )
            )

        if limit:
            targets = targets[:limit]

        logger.info(f"Using default user-specific targets: {len(targets)} items")
        return targets
