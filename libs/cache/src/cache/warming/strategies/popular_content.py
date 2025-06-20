"""Popular content warming strategy."""

import structlog
from typing import List, Optional, Dict, Any, Callable, Awaitable

from cache.warming.types import WarmingTarget, WarmingConfig, WarmingStrategy
from .base import BaseWarmingStrategy

logger = structlog.get_logger(__name__)


class PopularContentStrategy(BaseWarmingStrategy):
    """Generic warming strategy for popular and trending content.

    This strategy is content-agnostic and delegates target creation
    to application-specific target factories.
    """

    def __init__(
        self,
        config: WarmingConfig,
        popularity_provider: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None,
        target_factories: Optional[
            Dict[str, Callable[[Dict[str, Any]], List[WarmingTarget]]]
        ] = None,
    ):
        """Initialize popular content strategy.

        Args:
            config: Warming configuration
            popularity_provider: Function that returns popularity data
            target_factories: Dictionary mapping content types to target creation functions
                            e.g., {"movies": create_movie_targets, "actors": create_actor_targets}
        """
        super().__init__(config)
        self.strategy_type = WarmingStrategy.POPULAR_CONTENT
        self.popularity_provider = popularity_provider
        self.target_factories = target_factories or {}

    def register_target_factory(
        self,
        content_type: str,
        factory: Callable[[Dict[str, Any]], List[WarmingTarget]],
    ) -> None:
        """Register a target factory for a specific content type.

        Args:
            content_type: Type of content (e.g., "movies", "actors", "products")
            factory: Function that creates warming targets for items of this type
        """
        self.target_factories[content_type] = factory
        logger.debug(f"Registered target factory for content type: {content_type}")

    async def identify_targets(
        self, limit: Optional[int] = None, context: Optional[Dict[str, Any]] = None
    ) -> List[WarmingTarget]:
        """Identify warming targets based on popular content.

        Args:
            limit: Maximum number of targets to return
            context: Additional context with content preferences

        Returns:
            List of warming targets for popular content
        """
        if not self.popularity_provider:
            logger.warning(
                "No popularity provider available for popular content warming"
            )
            return await self._get_default_popular_targets(limit)

        try:
            ***REMOVED*** Get popularity data from application
            popularity_data = await self.popularity_provider()
            targets = []

            ***REMOVED*** Process different types of popular content using registered factories
            for content_type, items in popularity_data.items():
                if content_type in self.target_factories:
                    ***REMOVED*** Delegate target creation to application-specific factory
                    factory = self.target_factories[content_type]
                    for item in items:
                        try:
                            item_targets = factory(item)
                            targets.extend(item_targets)
                        except Exception as e:
                            logger.warning(
                                f"Error creating targets for {content_type} item {item.get('id', 'unknown')}: {e}"
                            )
                else:
                    logger.warning(
                        f"No target factory registered for content type: {content_type}"
                    )

            ***REMOVED*** Sort by priority and apply limit
            targets.sort(key=lambda t: t.priority, reverse=True)
            if limit:
                targets = targets[:limit]

            logger.info(
                f"Identified {len(targets)} popular content targets for warming"
            )
            return targets

        except Exception as e:
            logger.error(f"Error getting popularity data: {e}")
            return await self._get_default_popular_targets(limit)

    def calculate_priority(self, target_data: Dict[str, Any]) -> float:
        """Calculate priority based on popularity metrics.

        Args:
            target_data: Content popularity data

        Returns:
            Priority score
        """
        popularity_score = target_data.get("popularity_score", 1.0)
        view_count = target_data.get("view_count", 0)
        content_type = target_data.get("content_type", "unknown")

        ***REMOVED*** Base priority from popularity
        base_priority = popularity_score

        ***REMOVED*** Boost based on view count (logarithmic scale)
        import math

        view_boost = math.log10(max(view_count, 1)) / 10.0

        ***REMOVED*** Generic priority calculation - no content-specific logic
        return (base_priority + view_boost) * self.config.popular_content_weight

    async def _get_default_popular_targets(
        self, limit: Optional[int] = None
    ) -> List[WarmingTarget]:
        """Get default popular content targets when no provider is available.

        Args:
            limit: Maximum number of targets

        Returns:
            List of default warming targets (generic examples)
        """
        targets = []

        ***REMOVED*** Only include generic examples - no business-specific logic
        logger.info("Using default popular content targets (no provider available)")
        return targets
