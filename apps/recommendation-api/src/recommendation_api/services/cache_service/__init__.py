"""Cache service package for Recommendation API.

This package provides direct access to a configured cache manager instance
and cache warming functionality.
"""

***REMOVED*** Import background warming service
from recommendation_api.services.cache_service.background_warming_service import (
    BackgroundWarmingService,
    get_background_warming_service,
    start_background_warming,
    stop_background_warming,
)
from recommendation_api.services.cache_service.cache_service import (
    check_cache_health,
    close_cache,
    get_cache,
)
from recommendation_api.services.cache_service.warming.config import (
    get_recommendation_warming_config,
    get_recommendation_warming_settings,
)

***REMOVED*** Import warming components
from recommendation_api.services.cache_service.warming.service import (
    RecommendationWarmingService,
    configure_recommendation_warming,
    get_recommendation_warming_service,
)

***REMOVED*** For backward compatibility
get_cache_service = get_cache
close_cache_service = close_cache

__all__ = [
    "get_cache",
    "close_cache",
    "check_cache_health",
    ***REMOVED*** For backward compatibility
    "get_cache_service",
    "close_cache_service",
    ***REMOVED*** Warming components
    "RecommendationWarmingService",
    "get_recommendation_warming_service",
    "configure_recommendation_warming",
    "get_recommendation_warming_config",
    "get_recommendation_warming_settings",
    ***REMOVED*** Background warming
    "BackgroundWarmingService",
    "get_background_warming_service",
    "start_background_warming",
    "stop_background_warming",
]
