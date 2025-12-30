"""BFF Cache Services Package.

This package provides all cache-related functionality for the BFF API including:
- Direct access to a configured cache manager instance
- Background warming service for automatic cache warming
- Warming components (service, functions, providers, factories)
"""

from cache import CacheManager
from cache import get_cache_manager as _get_cache_manager
from cache.config import CacheSettings

from bff_api.config.app import get_cache_settings
from bff_api.services.cache_service.cache_service import (
    check_cache_health,
    close_cache,
    get_cache,
)

# Background warming service removed - using cron jobs for scheduled warming
# from bff_api.services.cache_service.background_warming_service import (
#     BackgroundWarmingService,
#     get_background_warming_service,
#     start_background_warming,
#     stop_background_warming,
# )
from bff_api.services.cache_service.warming import (
    BFFWarmingService,
    configure_bff_warming,
    get_bff_warming_config,
    get_bff_warming_service,
    get_bff_warming_settings,
)


# Dummy function for backward compatibility
def get_background_warming_service() -> None:
    """Dummy function - background warming service removed.

    Background warming has been disabled in favor of cron-based warming.
    This function exists for backward compatibility only.
    """
    return None


class BackgroundWarmingService:  # pragma: no cover
    """Backward compatible placeholder - background warming removed.

    The BFF now uses cron-based warming; this exists only to keep legacy imports working.
    """

    def __init__(self, *_: object, **__: object) -> None:
        return None


def start_background_warming(*_: object, **__: object) -> None:
    """Backward compatible no-op - background warming removed."""


def stop_background_warming(*_: object, **__: object) -> None:
    """Backward compatible no-op - background warming removed."""


def get_cache_manager(settings: CacheSettings | None = None) -> CacheManager:
    """Get a cache manager instance configured with BFF API settings.

    This function wraps the cache library's get_cache_manager function
    to ensure it uses the BFF API's cache settings by default.

    Args:
        settings: Optional cache settings to use instead of the default

    Returns:
        Configured cache manager instance
    """
    if settings is None:
        settings = get_cache_settings()

    return _get_cache_manager(settings)


# For backward compatibility
get_cache_service = get_cache
close_cache_service = close_cache

__all__ = [
    # Cache service
    "get_cache",
    "close_cache",
    "check_cache_health",
    # Background warming service
    "BackgroundWarmingService",
    "get_background_warming_service",
    "start_background_warming",
    "stop_background_warming",
    # Warming service
    "BFFWarmingService",
    "get_bff_warming_service",
    "configure_bff_warming",
    "get_bff_warming_config",
    "get_bff_warming_settings",
    # For backward compatibility
    "get_cache_service",
    "close_cache_service",
    "get_cache_manager",
]
