"""BFF Cache Services Package.

This package provides all cache-related functionality for the BFF API including:
- Direct access to a configured cache manager instance
- Background warming service for automatic cache warming
- Warming components (service, functions, providers, factories)
"""

from bff_api.services.cache_service.cache_service import (
    get_cache,
    close_cache,
    check_cache_health,
)
from bff_api.services.cache_service.background_warming_service import (
    BackgroundWarmingService,
    get_background_warming_service,
    start_background_warming,
    stop_background_warming,
)
from bff_api.services.cache_service.warming import (
    BFFWarmingService,
    get_bff_warming_service,
    configure_bff_warming,
    get_bff_warming_config,
    get_bff_warming_settings,
)

***REMOVED*** For backward compatibility
get_cache_service = get_cache
close_cache_service = close_cache

__all__ = [
    ***REMOVED*** Cache service
    "get_cache",
    "close_cache",
    "check_cache_health",
    ***REMOVED*** Background warming service
    "BackgroundWarmingService",
    "get_background_warming_service",
    "start_background_warming",
    "stop_background_warming",
    ***REMOVED*** Warming service
    "BFFWarmingService",
    "get_bff_warming_service",
    "configure_bff_warming",
    "get_bff_warming_config",
    "get_bff_warming_settings",
    ***REMOVED*** For backward compatibility
    "get_cache_service",
    "close_cache_service",
]
