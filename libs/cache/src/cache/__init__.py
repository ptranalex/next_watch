"""NextWatch Cache Library

A focused, production-ready Redis caching library for the NextWatch monorepo.
Provides typed cache keys, decorators, and domain-specific TTL management.
"""

from cache.config.settings import CacheSettings
from cache.manager import CacheManager
from cache.providers.redis import RedisProvider
from cache.decorators import redis_cache
from cache.keys import build_cache_key, build_filtered_key, build_paginated_key, hash_parameters
from cache.metrics import MetricsCollector, get_global_collector, set_metrics_enabled
from cache.warming import WarmingEngine, WarmingConfig, WarmingTarget, WarmingStrategy

__version__ = "0.1.0"
__all__ = [
    "CacheManager",
    "CacheSettings",
    "RedisProvider",
    "redis_cache",
    ***REMOVED*** Key building utilities
    "build_cache_key",
    "build_filtered_key",
    "build_paginated_key",
    "hash_parameters",
    ***REMOVED*** Metrics
    "MetricsCollector",
    "get_global_collector",
    "set_metrics_enabled",
    ***REMOVED*** Warming
    "WarmingEngine",
    "WarmingConfig",
    "WarmingTarget",
    "WarmingStrategy",
]
