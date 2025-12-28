"""Cache service for BFF API using the NextWatch cache library.

This module provides a clean integration using standardized environment variables.
Both BFF config and cache library read from the same environment variables,
eliminating any configuration translation or duplication.
"""

from cache import CacheManager, set_metrics_enabled
from config.logging import get_logger

from bff_api.config.app import get_cache_settings, settings
from bff_api.core.metrics import get_bff_metrics

logger = get_logger(__name__)

***REMOVED*** Global cache manager instance
_cache_manager: CacheManager | None = None


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
            if (
                hasattr(settings, "cache_enable_metrics")
                and settings.cache_enable_metrics
            ):
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


def record_cache_operation(operation: str, cache_name: str, status: str) -> None:
    """Record cache operation metrics.

    Args:
        operation: Cache operation (get, set, delete, clear)
        cache_name: Name of the cache
        status: Operation status (hit, miss, error)
    """
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_cache_operation(operation, cache_name, status)


def update_cache_hit_rate(cache_name: str, hit_rate: float) -> None:
    """Update cache hit rate metrics.

    Args:
        cache_name: Name of the cache
        hit_rate: Hit rate as percentage (0-100)
    """
    metrics = get_bff_metrics()
    if metrics:
        metrics.update_cache_hit_rate(cache_name, hit_rate)
