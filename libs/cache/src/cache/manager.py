"""Cache manager - main interface for the cache library."""

from typing import Any, Dict, List, Optional, TypeVar, cast

import structlog

from cache.config.settings import CacheSettings
from cache.providers.base import CacheProvider
from cache.providers.redis import RedisProvider
from cache.types import CacheKey, CacheResult, CacheSetResult, JSONSerializable, TTL

logger = structlog.get_logger(__name__)

***REMOVED*** Type variable for generic return types
T = TypeVar("T")


class CacheManager:
    """Main cache manager providing unified interface to cache operations."""

    def __init__(
        self, provider: CacheProvider, settings: Optional[CacheSettings] = None
    ) -> None:
        """Initialize cache manager.

        Args:
            provider: Cache provider implementation
            settings: Cache configuration settings (optional)
        """
        self.provider = provider
        self.settings = settings or CacheSettings()
        self.logger = logger.bind(
            manager="CacheManager", provider=provider.__class__.__name__
        )

        self.logger.info("Cache manager initialized")

    @classmethod
    def from_settings(cls, settings: Optional[CacheSettings] = None) -> "CacheManager":
        """Create cache manager from settings with Redis provider.

        Args:
            settings: Cache configuration settings

        Returns:
            Configured cache manager instance

        Raises:
            ValueError: If configuration validation fails
        """
        if settings is None:
            settings = CacheSettings()

        ***REMOVED*** Log cache configuration for debugging
        logger.info(
            "Cache manager created from environment variables",
            redis_url_masked=(
                settings.redis_url.replace("@", "@***")
                if "@" in settings.redis_url
                else settings.redis_url
            ),
            key_prefix=settings.cache_key_prefix,
            enable_metrics=settings.cache_enable_metrics,
        )

        provider = RedisProvider.from_settings(settings)
        return cls(provider=provider, settings=settings)

    ***REMOVED*** Core cache operations - delegate to provider
    async def get_json(self, key: CacheKey) -> CacheResult:
        """Get JSON value from cache.

        Args:
            key: The cache key

        Returns:
            The cached value as Python object, or None if not found
        """
        return await self.provider.get_json(key)

    async def set_json(
        self, key: CacheKey, value: JSONSerializable, ttl: TTL = None
    ) -> CacheSetResult:
        """Set JSON value in cache.

        Args:
            key: The cache key
            value: The value to cache (must be JSON serializable)
            ttl: Time to live in seconds, None for default TTL

        Returns:
            True if successful, False otherwise
        """
        ***REMOVED*** Use default TTL from settings if not specified
        if ttl is None:
            ttl = self.settings.cache_ttl_default

        return await self.provider.set_json(key, value, ttl)

    async def delete_key(self, key: CacheKey) -> bool:
        """Delete a key from cache.

        Args:
            key: The cache key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        return await self.provider.delete_key(key)

    async def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in cache.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """
        return await self.provider.exists(key)

    ***REMOVED*** Domain-specific TTL helpers
    def get_ttl_for_domain(self, domain: str) -> int:
        """Get TTL for a specific domain.

        Args:
            domain: Domain name (e.g., 'movie', 'user', 'popular')

        Returns:
            TTL in seconds for the domain
        """
        return self.settings.get_ttl_for_domain(domain)

    async def set_json_with_domain_ttl(
        self, key: CacheKey, value: JSONSerializable, domain: str
    ) -> CacheSetResult:
        """Set JSON value with domain-specific TTL.

        Args:
            key: The cache key
            value: The value to cache
            domain: Domain name for TTL lookup

        Returns:
            True if successful, False otherwise
        """
        ttl = self.get_ttl_for_domain(domain)
        return await self.set_json(key, value, ttl)

    ***REMOVED*** Enhanced methods with error handling and type safety
    async def get_json_safe(
        self, key: CacheKey, log_errors: bool = True
    ) -> Optional[JSONSerializable]:
        """Get JSON value from cache with error handling.

        Args:
            key: The cache key
            log_errors: Whether to log errors (default: True)

        Returns:
            The cached value or None if not found or on error
        """
        try:
            return await self.get_json(key)
        except Exception as e:
            if log_errors:
                self.logger.error(f"Failed to get cache key {key}", error=str(e))
            return None

    async def get_dict(
        self, key: CacheKey, log_errors: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get dictionary value from cache with type safety and error handling.

        Args:
            key: The cache key
            log_errors: Whether to log errors (default: True)

        Returns:
            The cached dictionary or None if not found, not a dict, or on error
        """
        try:
            result = await self.get_json(key)
            if isinstance(result, dict):
                return cast(Dict[str, Any], result)
            return None
        except Exception as e:
            if log_errors:
                self.logger.error(
                    f"Failed to get dict from cache key {key}", error=str(e)
                )
            return None

    async def get_list(
        self, key: CacheKey, log_errors: bool = True
    ) -> Optional[List[Any]]:
        """Get list value from cache with type safety and error handling.

        Args:
            key: The cache key
            log_errors: Whether to log errors (default: True)

        Returns:
            The cached list or None if not found, not a list, or on error
        """
        try:
            result = await self.get_json(key)
            if isinstance(result, list):
                return cast(List[Any], result)
            return None
        except Exception as e:
            if log_errors:
                self.logger.error(
                    f"Failed to get list from cache key {key}", error=str(e)
                )
            return None

    async def set_json_safe(
        self,
        key: CacheKey,
        value: JSONSerializable,
        ttl: TTL = None,
        log_errors: bool = True,
    ) -> bool:
        """Set JSON value in cache with error handling.

        Args:
            key: The cache key
            value: The value to cache (must be JSON serializable)
            ttl: Time to live in seconds, None for default TTL
            log_errors: Whether to log errors (default: True)

        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.set_json(key, value, ttl)
        except Exception as e:
            if log_errors:
                self.logger.error(f"Failed to set cache key {key}", error=str(e))
            return False

    async def delete_key_safe(self, key: CacheKey, log_errors: bool = True) -> bool:
        """Delete a key from cache with error handling.

        Args:
            key: The cache key to delete
            log_errors: Whether to log errors (default: True)

        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.delete_key(key)
        except Exception as e:
            if log_errors:
                self.logger.error(f"Failed to delete cache key {key}", error=str(e))
            return False

    ***REMOVED*** Health and management operations
    async def health_check(self) -> bool:
        """Perform health check on the cache system.

        Returns:
            True if healthy, False otherwise
        """
        try:
            healthy = await self.provider.health_check()
            if healthy:
                self.logger.debug("Cache health check passed")
            else:
                self.logger.warning("Cache health check failed")
            return healthy
        except Exception as e:
            self.logger.error("Cache health check error", error=str(e))
            return False

    async def close(self) -> None:
        """Close cache connections and cleanup resources.

        Should be called when shutting down the application.
        """
        self.logger.info("Closing cache manager")
        if hasattr(self.provider, "close"):
            await self.provider.close()

    ***REMOVED*** Context manager support
    async def __aenter__(self) -> "CacheManager":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Async context manager exit."""
        await self.close()
