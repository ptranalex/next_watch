"""BFF Smart Warming Integration.

This module integrates the smart warming service with FastAPI endpoints
to provide intelligent, event-driven cache warming based on user behavior.
Includes performance optimizations to prevent backend overload.
"""

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from cache.smart_warming import get_smart_warming_service
from config.logging import get_logger
from fastapi import BackgroundTasks

logger = get_logger(__name__)


@dataclass
class ConnectionPoolStats:
    """Statistics for backend connection pool."""

    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    last_reset: datetime | None = None

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
        self._shared_client: Any | None = None
        self._client_lock = asyncio.Lock()
        self._stats = ConnectionPoolStats()
        self._circuit_breaker_failures = 0
        self._circuit_breaker_opened_at: datetime | None = None
        self._circuit_breaker_threshold = 5  ***REMOVED*** failures before opening
        self._circuit_breaker_timeout = 60  ***REMOVED*** seconds before trying again

    async def get_client(self) -> Any:
        """Get a shared backend client with connection pooling."""
        async with self._client_lock:
            if self._shared_client is None:
                from fast_core.dependencies.client_factory import ServiceClientConfig

                from bff_api.config.app import settings
                from bff_api.services.clients import BackendClient

                backend_config = ServiceClientConfig(
                    name="backend",
                    base_url=settings.backend_api_url,
                    timeout=self.request_timeout,
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
    async def get_connection(self) -> AsyncIterator[Any]:
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

    def get_stats(self) -> dict[str, Any]:
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
_backend_connection_manager: BackendConnectionManager | None = None


def get_backend_connection_manager() -> BackendConnectionManager:
    """Get the global backend connection manager."""
    global _backend_connection_manager
    if _backend_connection_manager is None:
        from bff_api.config.app import get_bff_settings

        ***REMOVED*** Get settings (automatically loads .env and .env.local)
        settings = get_bff_settings()
        max_connections = getattr(settings, "warming_max_connections", 4)
        request_timeout = getattr(settings, "warming_request_timeout", 3)

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
        self._version_cache: dict[str, str] = {}  ***REMOVED*** Cache of known versions
        self._warming_in_progress: dict[str, asyncio.Event] = {}  ***REMOVED*** Prevent duplicate warming
        self._warming_lock = asyncio.Lock()

    async def check_version_needs_warming(
        self, resource_id: int, resource_type: str, current_version: str | None = None
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
        warming_func: Callable[[], Awaitable[dict[str, Any]]],
        version_getter: Callable[[int], Awaitable[str | None]] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
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
        from bff_api.config.app import get_bff_settings
        from bff_api.services.cache_service.warming.config import get_bff_warming_config

        self.smart_warmer = get_smart_warming_service()
        self.version_warmer = VersionAwareWarming()
        self.connection_manager = get_backend_connection_manager()
        self._warming_throttle: dict[str, datetime] = {}  ***REMOVED*** Throttle warming requests
        self._throttle_window = timedelta(seconds=30)  ***REMOVED*** Minimum time between warmings

        ***REMOVED*** Log warming configuration for debugging
        settings = get_bff_settings()  ***REMOVED*** Automatically loads .env and .env.local
        warming_config = get_bff_warming_config()

        env_config = {
            "WARMING_MAX_CONNECTIONS": getattr(settings, "warming_max_connections", 4),
            "WARMING_REQUEST_TIMEOUT": getattr(settings, "warming_request_timeout", 3),
            "WARMING_MAX_CONCURRENT": getattr(settings, "warming_max_concurrent", 3),
            "WARMING_OPERATION_TIMEOUT": getattr(settings, "warming_operation_timeout", 120),
            "WARMING_REQUESTS_PER_SECOND": getattr(settings, "warming_requests_per_second", 2),
            "WARMING_BURST_SIZE": getattr(settings, "warming_burst_size", 5),
            "WARMING_MAX_ITEMS_PER_STRATEGY": getattr(
                settings, "warming_max_items_per_strategy", 10000
            ),
        }

        logger.info(
            "🚀 BFF Smart Warming Configuration",
            warming_config={
                "max_concurrent_operations": warming_config.max_concurrent_operations,
                "operation_timeout_seconds": warming_config.operation_timeout_seconds,
                "max_items_per_strategy": warming_config.max_items_per_strategy,
                "min_miss_rate_threshold": warming_config.min_miss_rate_threshold,
                "strategies_enabled": {
                    "metrics_driven": warming_config.enable_metrics_driven,
                    "popular_content": warming_config.enable_popular_content,
                    "user_specific": warming_config.enable_user_specific,
                    "scheduled": warming_config.enable_scheduled,
                },
            },
            environment_config=env_config,
            connection_pool={
                "max_connections": self.connection_manager.max_connections,
                "request_timeout": self.connection_manager.request_timeout,
            },
            throttle_window_seconds=self._throttle_window.total_seconds(),
        )

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
        user_id: int | None = None,
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
                from bff_api.config.app import settings
                from bff_api.services.cache_service.warming.functions import (
                    WarmingFunctions,
                )

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

            from bff_api.config.app import settings
            from bff_api.services.cache_service.warming.functions import (
                WarmingFunctions,
            )

            async def get_movie_version(movie_id: int) -> str | None:
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

            async def movie_warming_func() -> dict[str, Any]:
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
        max_movies: int | None = None,  ***REMOVED*** Now optional for unlimited warming by default
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
            from bff_api.config.app import settings
            from bff_api.services.cache_service.warming.functions import (
                WarmingFunctions,
            )

            warming_funcs = WarmingFunctions(settings)

            try:
                ***REMOVED*** Safety warning for very high limits
                if max_movies and max_movies > 5000:
                    logger.warning(
                        "Very high max_movies limit - this may overwhelm the backend",
                        max_movies=max_movies,
                        tier=priority_tier,
                        recommendation="Consider starting with smaller batches",
                    )

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

                async def _warm_with_concurrency_limit(movie_id: int) -> dict[str, Any]:
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

    async def _get_tier_movie_ids(self, priority_tier: int, max_movies: int | None) -> list[int]:
        """Get movie IDs for a specific tier based on filtering criteria.

        Args:
            priority_tier: Priority tier (1, 2, or 3)
            max_movies: Maximum number of movies to return

        Returns:
            List of movie IDs for the tier
        """
        try:
            ***REMOVED*** Determine if we should use debugging limit or get all movies
            use_debug_limit = (
                max_movies is not None and max_movies < 10000
            )  ***REMOVED*** Assume limits < 10k are for debugging

            if priority_tier == 1:
                ***REMOVED*** Tier 1: New releases + trending (last 30 days)
                if use_debug_limit:
                    logger.info(
                        f"Fetching Tier 1: new releases and trending movies (DEBUG: limited to {max_movies})"
                    )
                    return await self._get_new_and_trending_movies(max_movies)
                else:
                    logger.info("Fetching Tier 1: new releases and trending movies (ALL available)")
                    return await self._get_new_and_trending_movies(None)  ***REMOVED*** None = no limit

            elif priority_tier == 2:
                ***REMOVED*** Tier 2: Popular movies + user favorites
                if use_debug_limit:
                    logger.info(
                        f"Fetching Tier 2: popular movies and user favorites (DEBUG: limited to {max_movies})"
                    )
                    return await self._get_popular_movies(max_movies)
                else:
                    logger.info(
                        "Fetching Tier 2: popular movies and user favorites (ALL available)"
                    )
                    return await self._get_popular_movies(None)  ***REMOVED*** None = no limit

            elif priority_tier == 3:
                ***REMOVED*** Tier 3: Full catalog for discovery
                if use_debug_limit:
                    logger.info(
                        f"Fetching Tier 3: full catalog for discovery (DEBUG: limited to {max_movies})"
                    )
                    discovery_ids = await self._get_all_available_movies()
                    return discovery_ids[:max_movies]  ***REMOVED*** Apply debug limit
                else:
                    logger.info("Fetching Tier 3: full catalog for discovery (ALL movies)")
                    discovery_ids = await self._get_all_available_movies()
                    logger.info(f"Tier 3 retrieved {len(discovery_ids)} total movies from database")
                    return discovery_ids

            else:
                logger.warning("Invalid priority tier", tier=priority_tier)
                return []

        except Exception as e:
            logger.error(
                "Failed to fetch tier movie IDs",
                tier=priority_tier,
                error=str(e),
                exc_info=True,
            )
            return []

    async def _get_new_and_trending_movies(self, max_movies: int | None) -> list[int]:
        """Get new releases and trending movies for Tier 1."""
        try:
            ***REMOVED*** Get actual movie IDs from backend instead of fake ranges
            async with self.connection_manager.get_connection() as backend_client:
                ***REMOVED*** Get movies - use unlimited fetch if no max_movies specified
                if max_movies is None:
                    ***REMOVED*** No limit - get all available movies and return the recent ones
                    all_movies = await self._get_all_available_movies()
                    logger.info(f"Retrieved {len(all_movies)} total movies for Tier 1 filtering")
                    return (
                        all_movies  ***REMOVED*** For Tier 1, return all (could add date filtering logic here)
                    )
                else:
                    ***REMOVED*** Limited fetch for debugging
                    movies_response = None
                    try:
                        ***REMOVED*** Try with sorting first
                        movies_response = await backend_client.get_movies(
                            page=1,
                            limit=max_movies,
                            sort_by="release_date",
                            sort_order="desc",
                        )
                    except Exception as sort_error:
                        logger.debug(f"Sorting not supported, trying basic call: {sort_error}")
                        ***REMOVED*** Fallback to basic call without sorting
                        movies_response = await backend_client.get_movies(page=1, limit=max_movies)

                movie_ids = []
                if movies_response and "results" in movies_response:
                    for movie in movies_response["results"]:
                        if isinstance(movie, dict) and "id" in movie:
                            movie_ids.append(movie["id"])

                logger.info(
                    f"Retrieved {len(movie_ids)} new/trending movies from backend (requested: {max_movies})"
                )
                return movie_ids[:max_movies] if max_movies else movie_ids

        except Exception as e:
            logger.warning(
                "Failed to get new/trending movies from backend, falling back to sample",
                error=str(e),
                max_movies=max_movies,
            )
            ***REMOVED*** Fallback: Get a smaller sample of existing movies
            return await self._get_fallback_movie_ids(min(max_movies, 100) if max_movies else 100)

    async def _get_popular_movies(self, max_movies: int | None) -> list[int]:
        """Get popular movies and user favorites for Tier 2."""
        try:
            ***REMOVED*** Get actual popular movies from backend
            async with self.connection_manager.get_connection() as backend_client:
                ***REMOVED*** Get movies - use unlimited fetch if no max_movies specified
                if max_movies is None:
                    ***REMOVED*** No limit - get all available movies
                    all_movies = await self._get_all_available_movies()
                    logger.info(f"Retrieved {len(all_movies)} total movies for Tier 2")
                    return all_movies
                else:
                    ***REMOVED*** Limited fetch for debugging
                    movies_response = None
                    try:
                        ***REMOVED*** Try with rating sorting first
                        movies_response = await backend_client.get_movies(
                            page=1,
                            limit=max_movies,
                            sort_by="rating",
                            sort_order="desc",
                        )
                    except Exception as sort_error:
                        logger.debug(
                            f"Rating sorting not supported, trying basic call: {sort_error}"
                        )
                        ***REMOVED*** Fallback to basic call without sorting
                        movies_response = await backend_client.get_movies(page=1, limit=max_movies)

                movie_ids = []
                if movies_response and "results" in movies_response:
                    for movie in movies_response["results"]:
                        if isinstance(movie, dict) and "id" in movie:
                            movie_ids.append(movie["id"])

                logger.info(
                    f"Retrieved {len(movie_ids)} popular movies from backend (requested: {max_movies})"
                )
                return movie_ids[:max_movies] if max_movies else movie_ids

        except Exception as e:
            logger.warning(
                "Failed to get popular movies from backend, falling back to sample",
                error=str(e),
                max_movies=max_movies,
            )
            ***REMOVED*** Fallback: Get a sample of existing movies
            return await self._get_fallback_movie_ids(min(max_movies, 200) if max_movies else 200)

    async def _get_discovery_movies(self, max_movies: int) -> list[int]:
        """Get full catalog movies for Tier 3 discovery."""
        try:
            ***REMOVED*** Get the full movie catalog from backend for discovery
            async with self.connection_manager.get_connection() as backend_client:
                ***REMOVED*** For discovery, get a diverse set - could be random or by various criteria
                ***REMOVED*** We'll paginate through movies to get up to max_movies
                all_movie_ids: list[int] = []
                page = 1
                page_size = min(100, max_movies)  ***REMOVED*** Backend API limit is 100 per request

                while len(all_movie_ids) < max_movies:
                    remaining = max_movies - len(all_movie_ids)
                    current_limit = min(page_size, remaining)

                    ***REMOVED*** Try basic get_movies call (without sorting to avoid 400 errors)
                    try:
                        logger.debug(f"Requesting page {page} with limit {current_limit}")
                        movies_response = await backend_client.get_movies(
                            page=page, limit=current_limit
                        )

                        ***REMOVED*** Log response metadata if available
                        if movies_response and isinstance(movies_response, dict):
                            total_in_response = movies_response.get("total", "unknown")
                            results_count = len(movies_response.get("results", []))
                            logger.debug(
                                f"Response metadata - total: {total_in_response}, results_in_page: {results_count}"
                            )

                    except Exception as api_error:
                        logger.warning(f"Failed to get page {page}: {api_error}")
                        break

                    if not movies_response or "results" not in movies_response:
                        logger.warning(
                            f"No response or results at page {page}, stopping pagination. Response: {movies_response}"
                        )
                        break

                    page_movie_ids = []
                    for movie in movies_response["results"]:
                        if isinstance(movie, dict) and "id" in movie:
                            page_movie_ids.append(movie["id"])

                    logger.debug(
                        f"Page {page}: fetched {len(page_movie_ids)} movies (cumulative: {len(all_movie_ids) + len(page_movie_ids)})"
                    )

                    if not page_movie_ids:  ***REMOVED*** No more movies
                        logger.warning(
                            f"No movie IDs found at page {page}, stopping pagination. Raw results: {movies_response.get('results', [])[:3] if movies_response else 'None'}"
                        )
                        break

                    all_movie_ids.extend(page_movie_ids)
                    page += 1

                    ***REMOVED*** Safety break to prevent infinite loops (increased for large datasets)
                    ***REMOVED*** Backend reports 179 total pages, so allow up to 200 for safety
                    max_pages = max(
                        (max_movies // page_size) + 10, 200
                    )  ***REMOVED*** Allow enough pages + buffer
                    if page > max_pages:
                        logger.warning(
                            f"Reached pagination limit at page {page} (max_pages: {max_pages})"
                        )
                        break

                logger.info(
                    f"Retrieved {len(all_movie_ids)} discovery movies from backend (requested: {max_movies}, pages_fetched: {page - 1})"
                )

                if len(all_movie_ids) < max_movies:
                    logger.warning(
                        f"Backend API returned {len(all_movie_ids)} movies, but {max_movies} were requested. "
                        f"This might indicate: 1) Database has fewer movies, 2) API pagination issue, "
                        f"3) Database query filtering some movies. Check backend logs for details."
                    )
                return all_movie_ids[:max_movies]

        except Exception as e:
            logger.warning(
                "Failed to get discovery movies from backend, falling back to sample",
                error=str(e),
                max_movies=max_movies,
            )
            ***REMOVED*** Fallback: Get whatever movies we can find
            return await self._get_fallback_movie_ids(min(max_movies, 500))

    async def _get_bulk_movie_ids(self, max_movies: int) -> list[int]:
        """Alternative method to get movie IDs using bulk endpoint approach."""
        try:
            async with self.connection_manager.get_connection() as backend_client:
                ***REMOVED*** Try using bulk endpoint with sequential ID ranges
                all_movie_ids: list[int] = []

                ***REMOVED*** Start with a reasonable ID range (most movie DBs start at 1)
                start_id = 1
                batch_size = 100

                while len(all_movie_ids) < max_movies and start_id < 10000:  ***REMOVED*** Safety limit
                    end_id = min(
                        start_id + batch_size - 1,
                        start_id + (max_movies - len(all_movie_ids)),
                    )
                    id_range = list(range(start_id, end_id + 1))

                    try:
                        ***REMOVED*** Use bulk endpoint if available
                        logger.debug(f"Trying bulk fetch for IDs {start_id}-{end_id}")
                        response = await backend_client.get_movies_bulk(id_range)

                        if response and "results" in response:
                            for movie in response["results"]:
                                if isinstance(movie, dict) and "id" in movie:
                                    all_movie_ids.append(movie["id"])

                        logger.debug(
                            f"Bulk fetch got {len(response.get('results', []))} movies for range {start_id}-{end_id}"
                        )

                    except Exception as bulk_error:
                        logger.debug(
                            f"Bulk fetch failed for range {start_id}-{end_id}: {bulk_error}"
                        )
                        ***REMOVED*** If bulk fails, this isn't the right approach for this backend
                        break

                    start_id = end_id + 1

                    ***REMOVED*** If we got fewer results than expected, we might be at the end
                    if response and len(response.get("results", [])) < batch_size:
                        logger.debug("Got fewer results than batch size, likely at end of data")
                        break

                logger.info(f"Bulk method retrieved {len(all_movie_ids)} movie IDs")
                return all_movie_ids

        except Exception as e:
            logger.warning(f"Bulk movie ID fetch failed: {e}")
            return []

    async def _get_all_available_movies(self) -> list[int]:
        """Get ALL available movies from the backend database (no limits for Tier 3)."""
        try:
            async with self.connection_manager.get_connection() as backend_client:
                all_movie_ids: list[int] = []
                page = 1
                page_size = 100  ***REMOVED*** Backend API limit is 100 per request
                total_pages_expected = None

                logger.info("Starting unlimited movie fetch for Tier 3 (full catalog)")

                while True:
                    try:
                        logger.debug(f"Fetching page {page} (page_size: {page_size})")
                        movies_response = await backend_client.get_movies(
                            page=page, limit=page_size
                        )

                        ***REMOVED*** Debug the actual response
                        if movies_response:
                            results_count = len(movies_response.get("results", []))
                            total_reported = movies_response.get("total", "unknown")
                            per_page_reported = movies_response.get("per_page", "unknown")
                            logger.debug(
                                f"API Response: got {results_count} results, total={total_reported}, per_page={per_page_reported}, requested_limit={page_size}"
                            )

                        ***REMOVED*** Log total pages on first response
                        if page == 1 and movies_response and isinstance(movies_response, dict):
                            total_in_response = movies_response.get("total", "unknown")
                            total_pages_in_response = movies_response.get("total_pages", "unknown")
                            logger.info(
                                f"Backend reports {total_in_response} total movies across {total_pages_in_response} pages"
                            )
                            total_pages_expected = total_pages_in_response

                        if not movies_response or "results" not in movies_response:
                            logger.info(f"No more data at page {page}, stopping")
                            break

                        page_movie_ids = []
                        for movie in movies_response["results"]:
                            if isinstance(movie, dict) and "id" in movie:
                                page_movie_ids.append(movie["id"])

                        if not page_movie_ids:
                            logger.info(f"No movie IDs found at page {page}, stopping")
                            break

                        all_movie_ids.extend(page_movie_ids)
                        logger.debug(
                            f"Page {page}: got {len(page_movie_ids)} movies (total: {len(all_movie_ids)})"
                        )

                        ***REMOVED*** If we got fewer results than page_size, we're at the end
                        if len(page_movie_ids) < page_size:
                            logger.info(
                                f"Last page reached at page {page} with {len(page_movie_ids)} movies"
                            )
                            break

                        page += 1

                        ***REMOVED*** Safety break - but much higher since we want everything
                        if page > 300:  ***REMOVED*** Should handle up to 30,000 movies
                            logger.warning(f"Reached safety limit at page {page}")
                            break

                    except Exception as api_error:
                        logger.warning(f"Failed to get page {page}: {api_error}")
                        break

                logger.info(
                    f"Unlimited fetch completed: {len(all_movie_ids)} movies from {page - 1} pages"
                )

                if total_pages_expected and page - 1 < total_pages_expected:
                    logger.warning(
                        f"Expected {total_pages_expected} pages but only got {page - 1} pages"
                    )

                return all_movie_ids

        except Exception as e:
            logger.error(f"Failed to get all available movies: {e}")
            ***REMOVED*** Fallback to the old discovery method with a high limit
            logger.info("Falling back to discovery method with high limit")
            return await self._get_discovery_movies(10000)

    async def _get_fallback_movie_ids(self, max_movies: int) -> list[int]:
        """Fallback method to get existing movie IDs safely.

        This method gets actual movie IDs from the backend when the tier-specific
        methods fail, ensuring we only warm movies that actually exist.
        """
        try:
            async with self.connection_manager.get_connection() as backend_client:
                ***REMOVED*** Get movies in small pages to find existing IDs
                all_movie_ids: list[int] = []
                page = 1
                page_size = 50  ***REMOVED*** Small pages for safety

                while len(all_movie_ids) < max_movies:
                    remaining = max_movies - len(all_movie_ids)
                    current_limit = min(page_size, remaining)

                    try:
                        ***REMOVED*** Try simplest possible API call to avoid parameter issues
                        if page == 1:
                            ***REMOVED*** First try - use limit parameter
                            movies_response = await backend_client.get_movies(
                                page=1, limit=current_limit
                            )
                        else:
                            ***REMOVED*** For pagination, some backends may not support it
                            movies_response = await backend_client.get_movies(
                                page=page, limit=current_limit
                            )

                        if not movies_response or "results" not in movies_response:
                            break

                        page_movie_ids = []
                        for movie in movies_response["results"]:
                            if isinstance(movie, dict) and "id" in movie:
                                page_movie_ids.append(movie["id"])

                        if not page_movie_ids:  ***REMOVED*** No more movies
                            break

                        all_movie_ids.extend(page_movie_ids)
                        page += 1

                        ***REMOVED*** Safety break (increased for large datasets)
                        max_fallback_pages = (max_movies // page_size) + 5
                        if page > max_fallback_pages:
                            logger.warning(f"Reached fallback pagination limit at page {page}")
                            break

                    except Exception as e:
                        logger.warning(f"Failed to get page {page} in fallback", error=str(e))
                        break

                logger.info(f"Fallback retrieved {len(all_movie_ids)} existing movie IDs")
                return all_movie_ids

        except Exception as e:
            logger.error(f"Complete fallback failure: {str(e)}")
            ***REMOVED*** Last resort: try the absolute simplest API call
            try:
                async with self.connection_manager.get_connection() as backend_client:
                    ***REMOVED*** Most basic call possible - no parameters
                    movies_response = await backend_client.get_movies()
                    if movies_response and "results" in movies_response:
                        movie_ids = []
                        for movie in movies_response["results"][:max_movies]:
                            if isinstance(movie, dict) and "id" in movie:
                                movie_ids.append(movie["id"])
                        if movie_ids:
                            logger.info(f"Emergency fallback got {len(movie_ids)} movies")
                            return movie_ids
            except Exception as emergency_error:
                logger.error(f"Emergency fallback failed: {emergency_error}")

            ***REMOVED*** Ultimate fallback: small safe range (only if all else fails)
            logger.warning("Using ultimate fallback: small ID range")
            return list(range(1, min(max_movies, 10) + 1))

    async def _warm_single_movie_with_version(
        self, movie_id: int, warming_funcs: Any, force: bool = False
    ) -> dict[str, Any]:
        """Warm a single movie with version checking."""

        async def get_movie_version(movie_id: int) -> str | None:
            """Get movie version for warming decision using connection manager."""
            try:
                ***REMOVED*** Use shared connection manager for version checks
                async with self.connection_manager.get_connection() as backend_client:
                    movie_data = await backend_client.get_movie(movie_id)

                    from bff_api.routes.v1.movies import _extract_movie_version

                    return _extract_movie_version(movie_data)
            except Exception:
                return None

        async def movie_warming_func() -> dict[str, Any]:
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
        user_id: int | None = None,
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
            from bff_api.config.app import settings
            from bff_api.services.cache_service.warming.functions import (
                WarmingFunctions,
            )

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
        user_id: int | None = None,
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
        resource_id: int | None = None,
        user_id: int | None = None,
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

    def get_warming_stats(self) -> dict[str, Any]:
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
_bff_smart_warming: BFFSmartWarming | None = None


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
