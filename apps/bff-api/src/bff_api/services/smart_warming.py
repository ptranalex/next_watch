"""BFF Smart Warming Integration.

This module integrates the smart warming service with FastAPI endpoints
to provide intelligent, event-driven cache warming based on user behavior.
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from fastapi import BackgroundTasks
import asyncio
import time

from cache.smart_warming import get_smart_warming_service, SmartWarmingService
from config.logging import get_logger

logger = get_logger(__name__)


class VersionAwareWarming:
    """Version-aware cache warming that only warms when versions change."""

    def __init__(self) -> None:
        """Initialize version-aware warming."""
        self._version_cache: Dict[str, str] = {}  ***REMOVED*** Cache of known versions

    async def check_version_needs_warming(
        self, resource_id: int, resource_type: str, current_version: Optional[str] = None
    ) -> bool:
        """Check if a resource needs warming based on version.

        Args:
            resource_id: ID of the resource
            resource_type: Type of resource (movie, genre, etc.)
            current_version: Current version of the resource

        Returns:
            True if warming is needed, False if cache is current
        """
        if not current_version:
            return True  ***REMOVED*** No version info, assume warming needed

        cache_key = f"{resource_type}:{resource_id}"
        cached_version = self._version_cache.get(cache_key)

        if cached_version != current_version:
            logger.debug(
                "Version change detected, warming needed",
                resource_type=resource_type,
                resource_id=resource_id,
                cached_version=cached_version,
                current_version=current_version,
            )
            self._version_cache[cache_key] = current_version
            return True

        logger.debug(
            "Version current, skipping warming",
            resource_type=resource_type,
            resource_id=resource_id,
            version=current_version,
        )
        return False

    async def warm_with_version_check(
        self,
        resource_id: int,
        resource_type: str,
        warming_func: Callable[[], Awaitable[Dict[str, Any]]],
        version_getter: Optional[Callable[[int], Awaitable[Optional[str]]]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Warm a resource only if its version has changed.

        Args:
            resource_id: ID of the resource to warm
            resource_type: Type of resource
            warming_func: Function to call for warming
            version_getter: Function to get current version
            force: Force warming regardless of version

        Returns:
            Warming result with version info
        """
        start_time = time.time()

        try:
            ***REMOVED*** Get current version if version_getter provided
            current_version = None
            if version_getter:
                try:
                    current_version = await version_getter(resource_id)
                except Exception as e:
                    logger.warning(
                        "Failed to get version, proceeding with warming",
                        resource_type=resource_type,
                        resource_id=resource_id,
                        error=str(e),
                    )

            ***REMOVED*** Check if warming needed (unless forced)
            if not force and current_version:
                needs_warming = await self.check_version_needs_warming(
                    resource_id, resource_type, current_version
                )
                if not needs_warming:
                    return {
                        "status": "skipped",
                        "reason": "version_current",
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "version": current_version,
                        "duration_ms": int((time.time() - start_time) * 1000),
                    }

            ***REMOVED*** Perform the warming
            logger.info(
                "Starting version-aware warming",
                resource_type=resource_type,
                resource_id=resource_id,
                version=current_version,
                forced=force,
            )

            warming_result = await warming_func()

            duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "Version-aware warming completed",
                resource_type=resource_type,
                resource_id=resource_id,
                version=current_version,
                duration_ms=duration_ms,
            )

            return {
                "status": "completed",
                "resource_id": resource_id,
                "resource_type": resource_type,
                "version": current_version,
                "duration_ms": duration_ms,
                "warming_result": warming_result,
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "Version-aware warming failed",
                resource_type=resource_type,
                resource_id=resource_id,
                error=str(e),
                duration_ms=duration_ms,
                exc_info=True,
            )

            return {
                "status": "failed",
                "resource_id": resource_id,
                "resource_type": resource_type,
                "error": str(e),
                "duration_ms": duration_ms,
            }


class BFFSmartWarming:
    """BFF-specific smart warming integration with version awareness."""

    def __init__(self) -> None:
        """Initialize BFF smart warming integration."""
        self.smart_warmer = get_smart_warming_service()
        self.version_warmer = VersionAwareWarming()
        logger.info("BFF smart warming integration initialized with version awareness")

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

    async def warm_movie_with_version_check(
        self,
        background_tasks: BackgroundTasks,
        movie_id: int,
        force: bool = False,
        **context: Any,
    ) -> None:
        """Warm movie data only if version has changed.

        This implements the "cache forever" strategy by checking if the movie
        version has changed before performing expensive warming operations.

        Args:
            background_tasks: FastAPI background tasks
            movie_id: Movie ID to warm
            force: Force warming regardless of version
            **context: Additional context
        """

        async def _version_aware_movie_warming() -> None:
            """Background task for version-aware movie warming."""
            from bff_api.services.cache_service.warming.functions import WarmingFunctions
            from bff_api.config.app import settings
            from bff_api.services.clients import BackendClient
            from fast_core.dependencies.client_factory import ServiceClientConfig

            async def get_movie_version(movie_id: int) -> Optional[str]:
                """Get current movie version from backend."""
                try:
                    ***REMOVED*** Create a lightweight backend client just for version checking
                    backend_config = ServiceClientConfig(
                        name="backend", base_url=settings.backend_api_url, timeout=10
                    )
                    backend_client = BackendClient(backend_config, settings)

                    ***REMOVED*** Get basic movie data to extract version
                    movie_data = await backend_client.get_movie(movie_id)

                    ***REMOVED*** Import version extraction function
                    from bff_api.routes.v1.movies import _extract_movie_version

                    return _extract_movie_version(movie_data)
                except Exception as e:
                    logger.warning(
                        "Failed to get movie version for warming",
                        movie_id=movie_id,
                        error=str(e),
                    )
                    return None

            async def movie_warming_func() -> Dict[str, Any]:
                """Execute the actual movie warming."""
                warming_funcs = WarmingFunctions(settings)
                return await warming_funcs.warm_movie_screen(movie_id)

            ***REMOVED*** Use version-aware warming
            result = await self.version_warmer.warm_with_version_check(
                resource_id=movie_id,
                resource_type="movie",
                warming_func=movie_warming_func,
                version_getter=get_movie_version,
                force=force,
            )

            logger.info(
                "Version-aware movie warming completed",
                movie_id=movie_id,
                result=result,
            )

        background_tasks.add_task(_version_aware_movie_warming)

        logger.debug(
            "Scheduled version-aware movie warming",
            movie_id=movie_id,
            force=force,
        )

    async def warm_priority_movies(
        self,
        background_tasks: BackgroundTasks,
        priority_tier: int = 1,
        max_movies: int = 50,
        force: bool = False,
        **context: Any,
    ) -> None:
        """Warm movies based on priority tiers from the strategy document.

        Tier 1 (every 2 hours): New releases (last 30 days), trending top 50
        Tier 2 (daily): Popular movies (top 500), user favorites
        Tier 3 (weekly): Full catalog refresh for discovery

        Args:
            background_tasks: FastAPI background tasks
            priority_tier: Priority tier (1, 2, or 3)
            max_movies: Maximum number of movies to warm
            force: Force warming regardless of version checks
            **context: Additional context
        """

        async def _priority_warming() -> None:
            """Background task for priority-based warming."""
            from bff_api.services.cache_service.warming.functions import WarmingFunctions
            from bff_api.config.app import settings

            warming_funcs = WarmingFunctions(settings)

            try:
                ***REMOVED*** Get movie IDs based on tier and max_movies parameter
                movie_ids = await self._get_tier_movie_ids(priority_tier, max_movies)

                if not movie_ids:
                    logger.warning("No movies found for tier", tier=priority_tier)
                    return

                ***REMOVED*** Use semaphore to limit concurrent backend connections
                max_concurrent = min(5, len(movie_ids))  ***REMOVED*** Cap at 5 concurrent requests

                logger.info(
                    "Starting tier warming",
                    tier=priority_tier,
                    total_movies=len(movie_ids),
                    max_requested=max_movies,
                    max_concurrent=max_concurrent,
                )

                ***REMOVED*** Warm movies with version checking to avoid redundant work
                semaphore = asyncio.Semaphore(max_concurrent)

                async def _warm_with_concurrency_limit(movie_id: int) -> Dict[str, Any]:
                    """Wrap warming with concurrency control."""
                    async with semaphore:
                        result = await self._warm_single_movie_with_version(
                            movie_id, warming_funcs, force=force
                        )
                        ***REMOVED*** Small delay to reduce backend load
                        await asyncio.sleep(0.1)
                        return result

                warming_tasks = [_warm_with_concurrency_limit(movie_id) for movie_id in movie_ids]

                ***REMOVED*** Execute warming tasks with bounded concurrency
                results = await asyncio.gather(*warming_tasks, return_exceptions=True)

                success_count = sum(
                    1 for r in results if isinstance(r, dict) and r.get("status") == "completed"
                )
                skip_count = sum(
                    1 for r in results if isinstance(r, dict) and r.get("status") == "skipped"
                )
                error_count = len(results) - success_count - skip_count

                logger.info(
                    "Priority warming completed",
                    tier=priority_tier,
                    total_movies=len(movie_ids),
                    success_count=success_count,
                    skip_count=skip_count,
                    error_count=error_count,
                )

            except Exception as e:
                logger.error(
                    "Priority warming failed",
                    tier=priority_tier,
                    error=str(e),
                    exc_info=True,
                )

        background_tasks.add_task(_priority_warming)

        logger.debug(
            "Scheduled priority warming",
            tier=priority_tier,
        )

    async def _get_tier_movie_ids(self, priority_tier: int, max_movies: int) -> List[int]:
        """Get movie IDs for a specific tier based on filtering criteria.

        Args:
            priority_tier: Priority tier (1, 2, or 3)
            max_movies: Maximum number of movies to return

        Returns:
            List of movie IDs for the tier
        """
        try:
            if priority_tier == 1:
                ***REMOVED*** Tier 1: New releases + trending (last 30 days)
                logger.info("Fetching Tier 1: new releases and trending movies")
                return await self._get_new_and_trending_movies(max_movies)

            elif priority_tier == 2:
                ***REMOVED*** Tier 2: Popular movies + user favorites
                logger.info("Fetching Tier 2: popular movies and user favorites")
                return await self._get_popular_movies(max_movies)

            elif priority_tier == 3:
                ***REMOVED*** Tier 3: Full catalog for discovery
                logger.info("Fetching Tier 3: full catalog for discovery")
                return await self._get_discovery_movies(max_movies)

            else:
                logger.warning("Invalid priority tier", tier=priority_tier)
                return []

        except Exception as e:
            logger.error(
                "Failed to fetch tier movie IDs", tier=priority_tier, error=str(e), exc_info=True
            )
            return []

    async def _get_new_and_trending_movies(self, max_movies: int) -> List[int]:
        """Get new releases and trending movies for Tier 1."""
        ***REMOVED*** For now, use a reasonable sample until backend integration
        ***REMOVED*** In production, this would call backend API for:
        ***REMOVED*** - Movies released in last 30 days
        ***REMOVED*** - Top trending movies
        sample_ids = list(range(1, min(max_movies + 1, 101)))
        logger.debug(f"Using sample new/trending movies: {len(sample_ids)} movies")
        return sample_ids

    async def _get_popular_movies(self, max_movies: int) -> List[int]:
        """Get popular movies and user favorites for Tier 2."""
        ***REMOVED*** In production, this would call backend API for:
        ***REMOVED*** - Top popular movies (by ratings, views)
        ***REMOVED*** - User favorites and watchlist items
        sample_ids = list(range(1, min(max_movies + 1, 501)))
        logger.debug(f"Using sample popular movies: {len(sample_ids)} movies")
        return sample_ids

    async def _get_discovery_movies(self, max_movies: int) -> List[int]:
        """Get full catalog movies for Tier 3 discovery."""
        ***REMOVED*** In production, this would call backend API for:
        ***REMOVED*** - Complete movie catalog
        ***REMOVED*** - Movies with good discovery potential
        sample_ids = list(range(1, min(max_movies + 1, 1001)))
        logger.debug(f"Using sample discovery movies: {len(sample_ids)} movies")
        return sample_ids

    async def _warm_single_movie_with_version(
        self, movie_id: int, warming_funcs: Any, force: bool = False
    ) -> Dict[str, Any]:
        """Warm a single movie with version checking."""
        from bff_api.services.clients import BackendClient
        from fast_core.dependencies.client_factory import ServiceClientConfig
        from bff_api.config.app import settings

        async def get_movie_version(movie_id: int) -> Optional[str]:
            """Get movie version for warming decision."""
            try:
                ***REMOVED*** Create client with shorter timeout for version checks
                backend_config = ServiceClientConfig(
                    name="backend", base_url=settings.backend_api_url, timeout=5
                )
                backend_client = BackendClient(backend_config, settings)
                movie_data = await backend_client.get_movie(movie_id)

                from bff_api.routes.v1.movies import _extract_movie_version

                return _extract_movie_version(movie_data)
            except Exception:
                return None

        async def movie_warming_func() -> Dict[str, Any]:
            """Execute movie warming."""
            result = await warming_funcs.warm_movie_screen(movie_id)
            return result if isinstance(result, dict) else {"result": result}

        return await self.version_warmer.warm_with_version_check(
            resource_id=movie_id,
            resource_type="movie",
            warming_func=movie_warming_func,
            version_getter=get_movie_version,
            force=force,
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
