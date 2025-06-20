"""Cache service for BFF API using the NextWatch cache library."""

from typing import Optional

from cache import CacheManager, get_global_collector, set_metrics_enabled
from cache.config import CacheSettings
from config.logging import get_logger

from bff_api.config.app import settings, get_cache_settings

logger = get_logger(__name__)

***REMOVED*** Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get or create the global cache manager instance.

    Returns:
        Global cache manager instance
    """
    global _cache_manager

    if _cache_manager is None:
        try:
            ***REMOVED*** Create cache settings from app settings
            cache_settings = get_cache_settings()

            _cache_manager = CacheManager.from_settings(cache_settings)

            ***REMOVED*** Enable metrics if configured
            if hasattr(settings, "cache_enable_metrics") and settings.cache_enable_metrics:
                set_metrics_enabled(True)
                logger.info("Cache metrics enabled")

            logger.info("Cache manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            ***REMOVED*** Create with default settings as fallback
            _cache_manager = CacheManager.from_settings()

    return _cache_manager


async def close_cache() -> None:
    """Close the global cache manager."""
    global _cache_manager

    if _cache_manager is not None:
        try:
            await _cache_manager.close()
            _cache_manager = None
            logger.info("Global cache manager closed")
        except Exception as e:
            logger.error(f"Error closing cache manager: {e}")


async def check_cache_health() -> bool:
    """Check if cache is healthy.

    Returns:
        True if cache is healthy, False otherwise
    """
    cache = get_cache()
    return await cache.health_check()
