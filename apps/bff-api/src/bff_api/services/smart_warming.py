"""BFF Smart Warming Integration.

This module integrates the smart warming service with FastAPI endpoints
to provide intelligent, event-driven cache warming based on user behavior.
"""

from typing import Dict, Any, Optional
from fastapi import BackgroundTasks

from cache.smart_warming import get_smart_warming_service, SmartWarmingService
from config.logging import get_logger

logger = get_logger(__name__)


class BFFSmartWarming:
    """BFF-specific smart warming integration."""

    def __init__(self) -> None:
        """Initialize BFF smart warming integration."""
        self.smart_warmer = get_smart_warming_service()
        logger.info("BFF smart warming integration initialized")

    async def warm_movie_interaction(
        self,
        background_tasks: BackgroundTasks,
        movie_id: int,
        user_id: Optional[int] = None,
        interaction_type: str = "viewed",
        **context: Any,
    ) -> None:
        """Warm content based on movie interaction.

        Args:
            background_tasks: FastAPI background tasks
            movie_id: ID of the movie
            user_id: Optional user ID
            interaction_type: Type of interaction (viewed, liked, added_to_watchlist)
            **context: Additional context (genre_id, rating, etc.)
        """

        async def _warm_movie_content() -> None:
            """Background task to warm movie-related content."""
            ***REMOVED*** Import here to avoid circular imports
            from bff_api.services.cache_service.warming.functions import WarmingFunctions
            from bff_api.config.app import settings

            async def warming_func() -> None:
                """Execute the actual movie warming."""
                warming_funcs = WarmingFunctions(settings)
                await warming_funcs.warm_movie_screen(movie_id)
                ***REMOVED*** Optionally warm related content based on context
                if genre_id := context.get("genre_id"):
                    await warming_funcs.warm_genre_screen(genre_id)

            await self.smart_warmer.warm_from_trigger(
                trigger_name=f"movie_{interaction_type}",
                warming_func=warming_func,
                user_id=user_id,
                movie_id=movie_id,
                **context,
            )

        background_tasks.add_task(_warm_movie_content)

        logger.debug(
            "Scheduled movie warming",
            movie_id=movie_id,
            user_id=user_id,
            interaction_type=interaction_type,
        )

    async def warm_genre_interaction(
        self,
        background_tasks: BackgroundTasks,
        genre_id: int,
        user_id: Optional[int] = None,
        **context: Any,
    ) -> None:
        """Warm content based on genre interaction.

        Args:
            background_tasks: FastAPI background tasks
            genre_id: ID of the genre
            user_id: Optional user ID
            **context: Additional context
        """

        async def _warm_genre_content() -> None:
            """Background task to warm genre-related content."""
            ***REMOVED*** Import here to avoid circular imports
            from bff_api.services.cache_service.warming.functions import WarmingFunctions
            from bff_api.config.app import settings

            async def warming_func() -> None:
                """Execute the actual genre warming."""
                warming_funcs = WarmingFunctions(settings)
                await warming_funcs.warm_genre_screen(genre_id)

            await self.smart_warmer.warm_from_trigger(
                trigger_name="genre_browsed",
                warming_func=warming_func,
                user_id=user_id,
                genre_id=genre_id,
                **context,
            )

        background_tasks.add_task(_warm_genre_content)

        logger.debug(
            "Scheduled genre warming",
            genre_id=genre_id,
            user_id=user_id,
        )

    async def warm_search_interaction(
        self,
        background_tasks: BackgroundTasks,
        query: str,
        user_id: Optional[int] = None,
        results_count: int = 0,
        **context: Any,
    ) -> None:
        """Warm content based on search interaction.

        Args:
            background_tasks: FastAPI background tasks
            query: Search query
            user_id: Optional user ID
            results_count: Number of results returned
            **context: Additional context
        """

        async def _warm_search_content() -> None:
            """Background task to warm search-related content."""

            async def warming_func() -> None:
                """Execute search-related warming - placeholder."""
                ***REMOVED*** TODO: Implement actual search warming logic
                logger.debug("Search warming placeholder", query=query)

            await self.smart_warmer.warm_from_trigger(
                trigger_name="search_performed",
                warming_func=warming_func,
                user_id=user_id,
                query=query,
                results_count=results_count,
                **context,
            )

        background_tasks.add_task(_warm_search_content)

        logger.debug(
            "Scheduled search warming",
            query=query,
            user_id=user_id,
            results_count=results_count,
        )

    async def warm_user_registration(
        self, background_tasks: BackgroundTasks, user_id: int, **context: Any
    ) -> None:
        """Warm content for new user registration.

        Args:
            background_tasks: FastAPI background tasks
            user_id: ID of the new user
            **context: Additional context (preferences, location, etc.)
        """

        async def _warm_new_user_content() -> None:
            """Background task to warm new user content."""

            async def warming_func() -> None:
                """Execute new user warming - placeholder."""
                ***REMOVED*** TODO: Implement actual new user warming logic
                logger.debug("New user warming placeholder", user_id=user_id)

            await self.smart_warmer.warm_from_trigger(
                trigger_name="user_registered",
                warming_func=warming_func,
                user_id=user_id,
                **context,
            )

        background_tasks.add_task(_warm_new_user_content)

        logger.debug(
            "Scheduled new user warming",
            user_id=user_id,
        )

    async def warm_on_cache_miss(
        self,
        background_tasks: BackgroundTasks,
        cache_key: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        user_id: Optional[int] = None,
        **context: Any,
    ) -> None:
        """Warm content when cache miss is detected.

        Args:
            background_tasks: FastAPI background tasks
            cache_key: The cache key that missed
            resource_type: Type of resource (movie, genre, actor, etc.)
            resource_id: Optional resource ID
            user_id: Optional user ID
            **context: Additional context
        """

        async def _warm_missed_content() -> None:
            """Background task to warm content after cache miss."""
            miss_context = {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                **context,
            }

            async def warming_func() -> None:
                """Execute cache miss warming - placeholder."""
                ***REMOVED*** TODO: Implement actual cache miss warming logic
                logger.debug(
                    "Cache miss warming placeholder",
                    resource_type=resource_type,
                    resource_id=resource_id,
                )

            await self.smart_warmer.warm_on_cache_miss(
                cache_key=cache_key, context=miss_context, warming_func=warming_func
            )

        background_tasks.add_task(_warm_missed_content)

        logger.debug(
            "Scheduled cache miss warming",
            cache_key=cache_key,
            resource_type=resource_type,
            resource_id=resource_id,
        )

    def get_warming_stats(self) -> Dict[str, Any]:
        """Get smart warming statistics.

        Returns:
            Dictionary with warming statistics
        """
        return self.smart_warmer.get_stats()

    def reset_warming_stats(self) -> None:
        """Reset smart warming statistics."""
        self.smart_warmer.reset_stats()


***REMOVED*** Global BFF smart warming instance
_bff_smart_warming: Optional[BFFSmartWarming] = None


def get_bff_smart_warming() -> BFFSmartWarming:
    """Get the global BFF smart warming instance.

    Returns:
        Global BFF smart warming instance
    """
    global _bff_smart_warming
    if _bff_smart_warming is None:
        _bff_smart_warming = BFFSmartWarming()
    return _bff_smart_warming


***REMOVED*** FastAPI dependency
async def get_smart_warming_dependency() -> BFFSmartWarming:
    """FastAPI dependency to get smart warming service.

    Returns:
        BFF smart warming instance
    """
    return get_bff_smart_warming()
