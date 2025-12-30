"""Cache dependency providers for FastAPI applications.

This module provides dependency providers for accessing cache services
and cache managers in FastAPI applications.
"""

from collections.abc import Callable
from typing import Any, cast

from config.logging import get_logger
from fastapi import Depends, Request

logger = get_logger(__name__)


def get_cache_manager() -> Any:
    """Get cache manager from app state.

    Returns:
        Dependency function that returns cache manager instance

    Raises:
        RuntimeError: If cache manager not found in app state
    """

    def _get_cache_manager(request: Request) -> Any:
        cache_manager = getattr(request.app.state, "cache_manager", None)
        if cache_manager is None:
            # Try to get from settings
            settings = getattr(request.app.state, "settings", None)
            if settings and hasattr(settings, "cache_manager"):
                cache_manager = settings.cache_manager

        if cache_manager is None:
            raise RuntimeError("Cache manager not found in app state")

        return cache_manager

    return Depends(_get_cache_manager)


def get_cache_provider(provider_name: str = "default") -> Any:
    """Get specific cache provider.

    Args:
        provider_name: Name of the cache provider

    Returns:
        Dependency function that returns cache provider instance

    Raises:
        RuntimeError: If cache provider not found
    """

    def _get_cache_provider(
        cache_manager: Any = Depends(get_cache_manager()),
    ) -> Any:
        try:
            if hasattr(cache_manager, "get_provider"):
                provider = cache_manager.get_provider(provider_name)
            elif hasattr(cache_manager, "providers"):
                provider = cache_manager.providers.get(provider_name)
            else:
                # Assume cache_manager is the provider itself
                provider = cache_manager

            if provider is None:
                raise RuntimeError(f"Cache provider '{provider_name}' not found")

            return provider
        except Exception as e:
            logger.error(f"Failed to get cache provider '{provider_name}': {e}")
            raise RuntimeError(f"Cache provider '{provider_name}' not available")

    return Depends(_get_cache_provider)


def get_redis_client() -> Any:
    """Get Redis client for direct Redis operations.

    Returns:
        Dependency function that returns Redis client instance

    Raises:
        RuntimeError: If Redis client not available
    """

    def _get_redis_client(request: Request) -> Any:
        # Try to get Redis client from app state
        redis_client = getattr(request.app.state, "redis_client", None)

        if redis_client is None:
            # Try to get from cache manager
            try:
                cache_manager = getattr(request.app.state, "cache_manager", None)
                if cache_manager and hasattr(cache_manager, "redis_client"):
                    redis_client = cache_manager.redis_client
                elif cache_manager and hasattr(cache_manager, "get_client"):
                    redis_client = cache_manager.get_client("redis")
            except Exception:
                pass

        if redis_client is None:
            raise RuntimeError("Redis client not available")

        return redis_client

    return Depends(_get_redis_client)


def get_cache_decorator() -> Any:
    """Get cache decorator for method caching.

    Returns:
        Dependency function that returns cache decorator function
    """

    def _get_cache_decorator(
        cache_manager: Any = Depends(get_cache_manager()),
    ) -> Callable[..., Any]:
        if hasattr(cache_manager, "cached"):
            return cast(Callable[..., Any], cache_manager.cached)
        elif hasattr(cache_manager, "cache"):
            return cast(Callable[..., Any], cache_manager.cache)
        else:
            # Return a no-op decorator if caching not available
            def no_op_cache(ttl: int = 300, **kwargs: Any) -> Callable[..., Any]:
                def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                    return func

                return decorator

            return no_op_cache

    return Depends(_get_cache_decorator)


class CacheService:
    """Service for cache operations with dependency injection."""

    def __init__(self, cache_manager: Any):
        """Initialize cache service.

        Args:
            cache_manager: Cache manager instance
        """
        self.cache_manager = cache_manager

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            if hasattr(self.cache_manager, "get"):
                return await self.cache_manager.get(key, default)
            return default
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            if hasattr(self.cache_manager, "set"):
                await self.cache_manager.set(key, value, ttl)
                return True
            return False
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if hasattr(self.cache_manager, "delete"):
                await self.cache_manager.delete(key)
                return True
            return False
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False


def get_cache_service() -> Any:
    """Get cache service instance.

    Returns:
        Dependency function that returns CacheService instance
    """

    def _get_cache_service(
        cache_manager: Any = Depends(get_cache_manager()),
    ) -> CacheService:
        return CacheService(cache_manager)

    return Depends(_get_cache_service)
