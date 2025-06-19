"""Cache service for BFF API using the NextWatch cache library."""

import logging
from typing import Any, Dict, Optional, cast

from cache import CacheManager, get_global_collector, set_metrics_enabled
from cache.config import CacheSettings
from cache.metrics import MetricsCollector
from cache.types import JSONSerializable
from config.logging import get_logger

from bff_api.config.app import settings

logger = get_logger(__name__)

***REMOVED*** Global cache service instance
_cache_service: Optional["CacheService"] = None


class CacheService:
    """Cache service wrapper for the NextWatch cache library."""

    def __init__(self, settings_obj: Optional[CacheSettings] = None):
        """Initialize cache service.

        Args:
            settings_obj: Optional cache settings. If None, will use default settings.
        """
        self.settings = settings_obj or CacheSettings()
        self.cache_manager = CacheManager.from_settings(self.settings)
        self._is_healthy = False

        ***REMOVED*** Enable metrics if configured
        if hasattr(settings, "cache_enable_metrics") and settings.cache_enable_metrics:
            set_metrics_enabled(True)
            logger.info("Cache metrics enabled")

    async def health_check(self) -> bool:
        """Check if cache service is healthy.

        Returns:
            True if cache is healthy, False otherwise
        """
        try:
            ***REMOVED*** Test basic cache operations
            test_key = "health_check_test"
            test_value: JSONSerializable = {"status": "ok", "timestamp": "test"}

            await self.cache_manager.set_json(test_key, test_value, ttl=10)
            result = await self.cache_manager.get_json(test_key)
            await self.cache_manager.delete_key(test_key)

            ***REMOVED*** Type-safe check for dictionary result
            if isinstance(result, dict) and result.get("status") == "ok":
                self._is_healthy = True
            else:
                self._is_healthy = False
            return self._is_healthy

        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            self._is_healthy = False
            return False

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON data from cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found
        """
        try:
            result = await self.cache_manager.get_json(key)
            ***REMOVED*** Type-safe conversion from JSONSerializable to Dict[str, Any]
            if isinstance(result, dict):
                return cast(Dict[str, Any], result)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    async def set_json(self, key: str, value: Dict[str, Any], ttl: int = 300) -> bool:
        """Set JSON data in cache.

        Args:
            key: Cache key
            value: Data to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.cache_manager.set_json(key, value, ttl=ttl)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    async def delete_key(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.cache_manager.delete_key(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    async def close(self) -> None:
        """Close cache service and cleanup resources."""
        try:
            if hasattr(self.cache_manager, "close"):
                await self.cache_manager.close()
            logger.info("Cache service closed successfully")
        except Exception as e:
            logger.error(f"Error closing cache service: {e}")

    @property
    def is_healthy(self) -> bool:
        """Check if cache service is healthy."""
        return self._is_healthy

    def get_metrics_collector(self) -> MetricsCollector:
        """Get the global metrics collector."""
        return get_global_collector()


def get_cache_service() -> CacheService:
    """Get or create the global cache service instance.

    Returns:
        Global cache service instance
    """
    global _cache_service

    if _cache_service is None:
        try:
            ***REMOVED*** Create cache settings from app settings
            from bff_api.config.app import get_cache_settings

            cache_settings = get_cache_settings()

            _cache_service = CacheService(cache_settings)
            logger.info("Cache service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize cache service: {e}")
            ***REMOVED*** Create with default settings as fallback
            _cache_service = CacheService()

    return _cache_service


async def close_cache_service() -> None:
    """Close the global cache service."""
    global _cache_service

    if _cache_service is not None:
        await _cache_service.close()
        _cache_service = None
        logger.info("Global cache service closed")
