"""BFF Smart Warming Integration.

This module integrates the smart warming service with FastAPI endpoints
to provide intelligent, event-driven cache warming based on user behavior.
Includes performance optimizations to prevent backend overload.
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from fastapi import BackgroundTasks
import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from cache.smart_warming import get_smart_warming_service, SmartWarmingService
from config.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionPoolStats:
    """Statistics for backend connection pool."""

    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    last_reset: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.last_reset is None:
            self.last_reset = datetime.now()


class BackendConnectionManager:
    """Manages shared backend connections to prevent overload."""

    def __init__(self, max_connections: int = 3, request_timeout: int = 5):
        """Initialize connection manager.

        Args:
            max_connections: Maximum concurrent backend connections
            request_timeout: Request timeout in seconds
        """
        self.max_connections = max_connections
        self.request_timeout = request_timeout
        self._semaphore = asyncio.Semaphore(max_connections)
        self._shared_client: Optional[Any] = None
        self._client_lock = asyncio.Lock()
        self._stats = ConnectionPoolStats()
        self._circuit_breaker_failures = 0
        self._circuit_breaker_opened_at: Optional[datetime] = None
        self._circuit_breaker_threshold = 5  ***REMOVED*** failures before opening
        self._circuit_breaker_timeout = 60  ***REMOVED*** seconds before trying again

    async def get_client(self) -> Any:
        """Get a shared backend client with connection pooling."""
        async with self._client_lock:
            if self._shared_client is None:
                from bff_api.services.clients import BackendClient
                from fast_core.dependencies.client_factory import ServiceClientConfig
                from bff_api.config.app import settings

                backend_config = ServiceClientConfig(
                    name="backend", base_url=settings.backend_api_url, timeout=self.request_timeout
                )
                self._shared_client = BackendClient(backend_config, settings)

        return self._shared_client

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self._circuit_breaker_opened_at is None:
            return False

        if datetime.now() - self._circuit_breaker_opened_at > timedelta(
            seconds=self._circuit_breaker_timeout
        ):
            ***REMOVED*** Reset circuit breaker after timeout
            self._circuit_breaker_opened_at = None
            self._circuit_breaker_failures = 0
            logger.info("Circuit breaker reset after timeout")
            return False

        return True

    def _record_failure(self) -> None:
        """Record a backend failure for circuit breaker."""
        self._circuit_breaker_failures += 1
        self._stats.failed_requests += 1

        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            self._circuit_breaker_opened_at = datetime.now()
            logger.warning(
                "Circuit breaker opened due to backend failures",
                failures=self._circuit_breaker_failures,
                threshold=self._circuit_breaker_threshold,
            )

    def _record_success(self) -> None:
        """Record a successful backend request."""
        self._circuit_breaker_failures = max(0, self._circuit_breaker_failures - 1)
        self._stats.total_requests += 1

    @asynccontextmanager
    async def get_connection(self) -> Any:
        """Get a rate-limited backend connection with circuit breaker."""
        if self._is_circuit_breaker_open():
            raise Exception("Backend circuit breaker is open")

        async with self._semaphore:
            self._stats.active_connections += 1
            start_time = time.time()

            try:
                client = await self.get_client()
                yield client

                ***REMOVED*** Record success
                duration_ms = (time.time() - start_time) * 1000
                self._record_success()

                ***REMOVED*** Update average response time
                total = self._stats.total_requests
                if total > 0:
                    self._stats.avg_response_time_ms = (
                        self._stats.avg_response_time_ms * (total - 1) + duration_ms
                    ) / total

            except Exception as e:
                self._record_failure()
                logger.warning(
                    "Backend connection failed",
                    error=str(e),
                    failures=self._circuit_breaker_failures,
                )
                raise
            finally:
                self._stats.active_connections -= 1

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            "active_connections": self._stats.active_connections,
            "max_connections": self.max_connections,
            "total_requests": self._stats.total_requests,
            "failed_requests": self._stats.failed_requests,
            "success_rate": (
                (self._stats.total_requests - self._stats.failed_requests)
                / max(1, self._stats.total_requests)
            )
            * 100,
            "avg_response_time_ms": self._stats.avg_response_time_ms,
            "circuit_breaker_open": self._is_circuit_breaker_open(),
            "circuit_breaker_failures": self._circuit_breaker_failures,
        }

    async def close(self) -> None:
        """Close the shared client and cleanup resources."""
        async with self._client_lock:
            if self._shared_client and hasattr(self._shared_client, "close"):
                try:
                    await self._shared_client.close()
                except Exception as e:
                    logger.warning("Error closing backend client", error=str(e))
            self._shared_client = None


***REMOVED*** Global connection manager
_backend_connection_manager: Optional[BackendConnectionManager] = None


def get_backend_connection_manager() -> BackendConnectionManager:
    """Get the global backend connection manager."""
    global _backend_connection_manager
    if _backend_connection_manager is None:
        import os

        ***REMOVED*** Allow configuration via environment variables
        max_connections = int(os.getenv("WARMING_MAX_CONNECTIONS", "4"))
        request_timeout = int(os.getenv("WARMING_REQUEST_TIMEOUT", "3"))

        _backend_connection_manager = BackendConnectionManager(
            max_connections=max_connections,  ***REMOVED*** Configurable via WARMING_MAX_CONNECTIONS
            request_timeout=request_timeout,  ***REMOVED*** Configurable via WARMING_REQUEST_TIMEOUT
        )

        logger.info(
            "Backend connection manager initialized",
            max_connections=max_connections,
            request_timeout=request_timeout,
        )
    return _backend_connection_manager


class VersionAwareWarming:
    """Version-aware cache warming that only warms when versions change."""

    def __init__(self) -> None:
        """Initialize version-aware warming."""
        self._version_cache: Dict[str, str] = {}  ***REMOVED*** Cache of known versions
        self._warming_in_progress: Dict[str, asyncio.Event] = {}  ***REMOVED*** Prevent duplicate warming
        self._warming_lock = asyncio.Lock()

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
        warming_key = f"{resource_type}:{resource_id}"

        try:
            ***REMOVED*** Check if warming is already in progress for this resource
            async with self._warming_lock:
                if warming_key in self._warming_in_progress:
                    logger.debug(
                        "Warming already in progress, waiting",
                        resource_type=resource_type,
                        resource_id=resource_id,
                    )
                    ***REMOVED*** Wait for the ongoing warming to complete
                    await self._warming_in_progress[warming_key].wait()
                    return {
                        "status": "deduped",
                        "reason": "warming_in_progress",
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "duration_ms": int((time.time() - start_time) * 1000),
                    }

                ***REMOVED*** Mark warming as in progress
                warming_event = asyncio.Event()
                self._warming_in_progress[warming_key] = warming_event

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

            finally:
                ***REMOVED*** Mark warming as complete and remove from progress tracking
                warming_event.set()
                async with self._warming_lock:
                    self._warming_in_progress.pop(warming_key, None)

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
        self.connection_manager = get_backend_connection_manager()
        self._warming_throttle: Dict[str, datetime] = {}  ***REMOVED*** Throttle warming requests
        self._throttle_window = timedelta(seconds=30)  ***REMOVED*** Minimum time between warmings
        logger.info(
            "BFF smart warming integration initialized with version awareness and connection management"
        )

    def _should_throttle_warming(self, throttle_key: str) -> bool:
        """Check if warming should be throttled based on recent activity."""
        now = datetime.now()
        last_warming = self._warming_throttle.get(throttle_key)

        if last_warming and (now - last_warming) < self._throttle_window:
            return True

        self._warming_throttle[throttle_key] = now
        return False

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
        ***REMOVED*** Apply throttling to prevent overwhelming backend
        throttle_key = f"movie_interaction:{movie_id}:{interaction_type}"
        if self._should_throttle_warming(throttle_key):
            logger.debug(
                "Movie interaction warming throttled",
                movie_id=movie_id,
                interaction_type=interaction_type,
                throttle_window_seconds=self._throttle_window.total_seconds(),
            )
            return

        async def _warm_movie_content() -> None:
            """Background task to warm movie-related content."""
            try:
                ***REMOVED*** Import here to avoid circular imports
                from bff_api.services.cache_service.warming.functions import WarmingFunctions
                from bff_api.config.app import settings

                async def warming_func() -> None:
                    """Execute the actual movie warming."""
                    warming_funcs = WarmingFunctions(settings)
                    await warming_funcs.warm_movie_screen(movie_id)
                    ***REMOVED*** Reduce cascade warming - only warm genre if explicitly requested
                    if context.get("warm_genre", False) and (genre_id := context.get("genre_id")):
                        await warming_funcs.warm_genre_screen(genre_id)

                await self.smart_warmer.warm_from_trigger(
                    trigger_name=f"movie_{interaction_type}",
                    warming_func=warming_func,
                    user_id=user_id,
                    movie_id=movie_id,
                    **context,
                )
            except Exception as e:
                logger.error(
                    "Movie interaction warming failed",
                    movie_id=movie_id,
                    error=str(e),
                    exc_info=True,
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
                """Get current movie version from backend using connection manager."""
                try:
                    ***REMOVED*** Use shared connection manager to prevent overload
                    async with self.connection_manager.get_connection() as backend_client:
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

                ***REMOVED*** Use controlled concurrency to balance speed and stability
                max_concurrent = min(
                    4, len(movie_ids)
                )  ***REMOVED*** Increased from 2 to 4 for better performance

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
            """Get movie version for warming decision using connection manager."""
            try:
                ***REMOVED*** Use shared connection manager for version checks
                async with self.connection_manager.get_connection() as backend_client:
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
        """Get smart warming statistics including connection pool stats.

        Returns:
            Dictionary with warming statistics
        """
        smart_stats = self.smart_warmer.get_stats()
        connection_stats = self.connection_manager.get_stats()

        return {
            **smart_stats,
            "backend_connections": connection_stats,
            "warming_throttle_entries": len(self._warming_throttle),
            "throttle_window_seconds": self._throttle_window.total_seconds(),
        }

    def reset_warming_stats(self) -> None:
        """Reset smart warming statistics."""
        self.smart_warmer.reset_stats()
        ***REMOVED*** Also clear throttle cache
        self._warming_throttle.clear()

    async def cleanup(self) -> None:
        """Clean up resources and close connections."""
        try:
            await self.connection_manager.close()
            self._warming_throttle.clear()
            logger.info("BFF smart warming cleanup completed")
        except Exception as e:
            logger.error("Error during BFF smart warming cleanup", error=str(e), exc_info=True)


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
