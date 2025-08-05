"""BFF-specific cache warming functions.

This module implements the actual warming functions that call the cached BFF endpoints.
"""

import asyncio
import random
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, time

from config.logging import get_logger
from fast_core.dependencies.client_factory import ServiceClientConfig

from bff_api.services.clients.facade import BackendClient
from bff_api.services.clients.recommendation import RecommendationClient
from bff_api.services.cache_service.warming.config import (
    WarmingRateLimiter,
    get_warming_rate_limits,
)
from bff_api.config.app import settings, BFFAPIConfig

logger = get_logger(__name__)

***REMOVED*** Global rate limiter for warming operations
_global_warming_rate_limiter: Optional[WarmingRateLimiter] = None


def get_warming_rate_limiter() -> WarmingRateLimiter:
    """Get or create the global warming rate limiter."""
    global _global_warming_rate_limiter
    if _global_warming_rate_limiter is None:
        rate_limits = get_warming_rate_limits()
        _global_warming_rate_limiter = WarmingRateLimiter(
            requests_per_second=float(rate_limits["requests_per_second"]),
            burst_size=int(rate_limits["burst_size"]),
        )
    return _global_warming_rate_limiter


async def _rate_limited_operation(
    operation_name: str, operation_func: Callable[[], Awaitable[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Execute an operation with rate limiting and backoff.

    Args:
        operation_name: Name of the operation for logging
        operation_func: Async function to execute

    Returns:
        Result of the operation

    Raises:
        Exception: If operation fails after retries
    """
    rate_limiter = get_warming_rate_limiter()
    rate_limits = get_warming_rate_limits()
    max_retries = 3
    base_delay = rate_limits["backoff_base"]
    max_delay = rate_limits["backoff_max"]
    use_jitter = rate_limits["jitter"]

    for attempt in range(max_retries + 1):
        try:
            ***REMOVED*** Apply rate limiting before each attempt
            await rate_limiter.acquire()

            logger.debug(
                f"Executing rate-limited warming operation",
                operation=operation_name,
                attempt=attempt + 1,
                max_retries=max_retries + 1,
            )

            ***REMOVED*** Execute the operation
            result = await operation_func()

            if attempt > 0:
                logger.info(
                    f"Rate-limited operation succeeded after retries",
                    operation=operation_name,
                    attempts=attempt + 1,
                )

            return result

        except Exception as e:
            is_rate_limit_error = "429" in str(e) or "Too Many Requests" in str(e)
            is_last_attempt = attempt == max_retries

            if is_rate_limit_error and not is_last_attempt:
                ***REMOVED*** Calculate exponential backoff with jitter
                delay = min(base_delay**attempt, max_delay)
                if use_jitter:
                    delay *= 0.5 + random.random() * 0.5  ***REMOVED*** Add 0-50% jitter

                logger.warning(
                    f"Rate limited during warming operation, retrying",
                    operation=operation_name,
                    attempt=attempt + 1,
                    max_retries=max_retries + 1,
                    delay_seconds=delay,
                    error=str(e),
                )

                await asyncio.sleep(delay)
                continue
            else:
                ***REMOVED*** Non-rate-limit error or final attempt
                if is_last_attempt:
                    logger.error(
                        f"Warming operation failed after all retries",
                        operation=operation_name,
                        attempts=attempt + 1,
                        error=str(e),
                    )
                else:
                    logger.error(
                        f"Warming operation failed with non-retryable error",
                        operation=operation_name,
                        attempt=attempt + 1,
                        error=str(e),
                    )
                raise

    ***REMOVED*** This should never be reached, but add for type safety
    raise Exception(f"Rate-limited operation {operation_name} failed after all attempts")


class WarmingFunctions:
    """Collection of warming functions for BFF cache."""

    def __init__(self, settings: BFFAPIConfig) -> None:
        """Initialize warming functions with settings."""
        self.settings = settings

    async def warm_movie_screen(
        self, movie_id: int, user_id: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm the movie screen data cache.

        Args:
            movie_id: ID of the movie to warm
            user_id: Optional user ID for user-specific data
            **kwargs: Additional warming parameters

        Returns:
            Dictionary containing warming results
        """

        async def _warm_operation() -> Dict[str, Any]:
            ***REMOVED*** Import the cached function dynamically to avoid circular imports
            from bff_api.routes.v1.movies import _get_movie_screen_data

            ***REMOVED*** Create client configurations
            backend_config = ServiceClientConfig(
                name="backend", base_url=self.settings.backend_api_url, timeout=30
            )
            recommendation_config = ServiceClientConfig(
                name="recommendation", base_url=self.settings.reco_api_url, timeout=30
            )

            ***REMOVED*** Create client instances
            backend_client = BackendClient(backend_config, self.settings)
            recommendation_client = RecommendationClient(recommendation_config, self.settings)

            ***REMOVED*** Warm the movie screen data (this will populate the cache)
            warmed_data = await _get_movie_screen_data(
                movie_id=movie_id,
                user_id=user_id,
                backend=backend_client,
                recommendation_client=recommendation_client,
                credentials=None,
            )

            return {
                "movie_id": movie_id,
                "user_id": user_id,
                "cache_populated": True,
                "data_size": len(str(warmed_data)) if warmed_data else 0,
            }

        result = await _rate_limited_operation(f"warm_movie_screen_{movie_id}", _warm_operation)
        return result

    async def warm_movies_list(
        self,
        genre_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Warm the movies list cache.

        Args:
            genre_id: Optional genre filter
            user_id: Optional user ID for personalization
            limit: Number of movies to fetch
            **kwargs: Additional warming parameters

        Returns:
            Dictionary containing warming results
        """

        async def _warm_operation() -> Dict[str, Any]:
            ***REMOVED*** Import the cached function dynamically to avoid circular imports
            from bff_api.routes.v1.movies import _get_movies_list_data

            ***REMOVED*** Create client configurations
            backend_config = ServiceClientConfig(
                name="backend", base_url=self.settings.backend_api_url, timeout=30
            )

            ***REMOVED*** Create client instance
            backend_client = BackendClient(backend_config, self.settings)

            ***REMOVED*** Warm the movies list data with correct signature
            warmed_data = await _get_movies_list_data(
                page=1,  ***REMOVED*** Start with page 1
                limit=limit,
                genre_id=genre_id,
                actor_id=None,
                sort_by="imdb_rating",
                sort_desc=True,
                imdb_rating=None,
                rotten_tomatoes_rating=None,
                metacritic_rating=None,
                year=None,
                start_year=None,
                end_year=None,
                user_id=user_id,
                backend=backend_client,
                credentials=None,
            )

            return {
                "genre_id": genre_id,
                "user_id": user_id,
                "limit": limit,
                "cache_populated": True,
                "movies_count": len(warmed_data.get("results", [])) if warmed_data else 0,
            }

        return await _rate_limited_operation(
            f"warm_movies_list_{genre_id}_{limit}", _warm_operation
        )

    async def warm_actor_screen(
        self, actor_id: int, user_id: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm the actor screen data cache.

        Args:
            actor_id: ID of the actor to warm
            user_id: Optional user ID for user-specific data (not used by underlying API)
            **kwargs: Additional warming parameters

        Returns:
            Dictionary containing warming results
        """

        async def _warm_operation() -> Dict[str, Any]:
            ***REMOVED*** Import the cached function dynamically to avoid circular imports
            from bff_api.routes.v1.actors import _get_actor_screen_data

            ***REMOVED*** Create client configurations
            backend_config = ServiceClientConfig(
                name="backend", base_url=self.settings.backend_api_url, timeout=30
            )

            ***REMOVED*** Create client instance
            backend_client = BackendClient(backend_config, self.settings)

            ***REMOVED*** Warm the actor screen data with correct signature
            warmed_data = await _get_actor_screen_data(
                actor_id=actor_id,
                page=1,
                limit=20,
                backend=backend_client,
                credentials=None,
            )

            return {
                "actor_id": actor_id,
                "user_id": user_id,
                "cache_populated": True,
                "data_size": len(str(warmed_data)) if warmed_data else 0,
            }

        return await _rate_limited_operation(f"warm_actor_screen_{actor_id}", _warm_operation)

    async def warm_genre_screen(
        self, genre_id: int, user_id: Optional[int] = None, limit: int = 20, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm the genre screen data cache.

        Args:
            genre_id: ID of the genre to warm
            user_id: Optional user ID for personalization
            limit: Number of movies to fetch
            **kwargs: Additional warming parameters

        Returns:
            Dictionary containing warming results
        """

        async def _warm_operation() -> Dict[str, Any]:
            ***REMOVED*** Import the cached function dynamically to avoid circular imports
            from bff_api.routes.v1.genres import _get_genre_screen_data

            ***REMOVED*** Create client configurations
            backend_config = ServiceClientConfig(
                name="backend", base_url=self.settings.backend_api_url, timeout=30
            )

            ***REMOVED*** Create client instance
            backend_client = BackendClient(backend_config, self.settings)

            ***REMOVED*** Warm the genre screen data with correct signature
            warmed_data = await _get_genre_screen_data(
                genre_id=genre_id,
                page=1,
                limit=limit,
                actor_id=None,
                sort_by="imdb_rating",
                sort_desc=True,
                imdb_rating=None,
                rotten_tomatoes_rating=None,
                metacritic_rating=None,
                year=None,
                start_year=None,
                end_year=None,
                user_id=user_id,
                backend=backend_client,
                credentials=None,
            )

            return {
                "genre_id": genre_id,
                "user_id": user_id,
                "limit": limit,
                "cache_populated": True,
                "movies_count": (
                    len(warmed_data.get("movies", {}).get("results", [])) if warmed_data else 0
                ),
            }

        return await _rate_limited_operation(
            f"warm_genre_screen_{genre_id}_{limit}", _warm_operation
        )
