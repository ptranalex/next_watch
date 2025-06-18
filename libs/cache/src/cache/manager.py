"""Cache manager - main interface for the cache library."""

from typing import Optional

import structlog

from cache.config.settings import CacheSettings
from cache.providers.base import CacheProvider
from cache.providers.redis import RedisProvider
from cache.types import CacheKey, CacheResult, CacheSetResult, JSONSerializable, TTL

logger = structlog.get_logger(__name__)


class CacheManager:
    """Main cache manager providing unified interface to cache operations."""

    def __init__(self, provider: CacheProvider, settings: Optional[CacheSettings] = None) -> None:
        """Initialize cache manager.

        Args:
            provider: Cache provider implementation
            settings: Cache configuration settings (optional)
        """
        self.provider = provider
        self.settings = settings or CacheSettings()
        self.logger = logger.bind(manager="CacheManager", provider=provider.__class__.__name__)

        self.logger.info("Cache manager initialized")

    @classmethod
    def from_settings(cls, settings: Optional[CacheSettings] = None) -> "CacheManager":
        """Create cache manager from settings with Redis provider.

        Args:
            settings: Cache configuration settings

        Returns:
            Configured cache manager instance
        """
        if settings is None:
            settings = CacheSettings()

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
        ***REMOVED*** Use default TTL if not specified
        if ttl is None:
            ttl = self.settings.ttl_default

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
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]
    ) -> None:
        """Async context manager exit."""
        await self.close()
