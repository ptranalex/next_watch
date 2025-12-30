"""NextWatch Cache Library

A focused, production-ready Redis caching library for the NextWatch monorepo.
Provides typed cache keys, decorators, and domain-specific TTL management.

Enhanced features:
- Type-safe methods (get_dict, get_list)
- Built-in error handling (_safe methods)
- Service-ready interfaces
"""

from cache.config.settings import CacheSettings
from cache.decorators import redis_cache
from cache.keys import (
    build_cache_key,
    build_filtered_key,
    build_paginated_key,
    hash_parameters,
)
from cache.manager import CacheManager, get_cache_manager
from cache.metrics import MetricsCollector, get_global_collector, set_metrics_enabled
from cache.providers.redis import RedisProvider
from cache.warming import WarmingConfig, WarmingEngine, WarmingStrategy, WarmingTarget

__version__ = "0.1.0"
__all__ = [
    "CacheManager",
    "CacheSettings",
    "RedisProvider",
    "redis_cache",
    # Key building utilities
    "build_cache_key",
    "build_filtered_key",
    "build_paginated_key",
    "hash_parameters",
    # Metrics
    "MetricsCollector",
    "get_global_collector",
    "set_metrics_enabled",
    # Warming
    "WarmingEngine",
    "WarmingConfig",
    "WarmingTarget",
    "WarmingStrategy",
    "get_cache_manager",
]
