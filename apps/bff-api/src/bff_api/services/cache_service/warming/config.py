"""BFF Cache Warming Configuration.

This module handles all configuration settings and setup for the BFF cache warming system.
"""

import asyncio
from typing import Any

from cache.warming import WarmingConfig

from bff_api.config.app import get_bff_settings


def get_bff_warming_config() -> WarmingConfig:
    """Get BFF-specific warming configuration.

    Uses the centralized settings object which automatically loads .env and .env.local
    following the same pattern as the Search API.

    Returns:
        Configured WarmingConfig instance with BFF-specific settings
    """
    ***REMOVED*** Get settings (automatically loads .env and .env.local)
    settings = get_bff_settings()

    ***REMOVED*** Use settings object with appropriate defaults
    max_concurrent = getattr(settings, "warming_max_concurrent", 3)
    max_items = getattr(settings, "warming_max_items_per_strategy", 10000)
    operation_timeout = getattr(settings, "warming_operation_timeout", 120)

    return WarmingConfig(
        ***REMOVED*** Rate limiting for downstream services - check env vars first
        max_concurrent_operations=max_concurrent,
        max_items_per_strategy=max_items,
        ***REMOVED*** Increased timeout for rate-limited operations
        operation_timeout_seconds=operation_timeout,
        min_miss_rate_threshold=getattr(settings, "warming_min_miss_rate", 0.3),
        min_avg_miss_time_ms=getattr(settings, "warming_min_avg_miss_time", 100.0),
        min_total_calls=getattr(settings, "warming_min_total_calls", 10),
        ***REMOVED*** Strategy configuration - Enable user_specific for BFF
        enable_metrics_driven=True,
        enable_popular_content=True,
        enable_user_specific=True,  ***REMOVED*** Enable for BFF
        enable_scheduled=True,
        ***REMOVED*** Strategy weights
        metrics_driven_weight=1.0,
        popular_content_weight=0.8,
        user_specific_weight=0.6,
        scheduled_weight=0.7,
    )


def get_warming_rate_limits() -> dict[str, Any]:
    """Get rate limiting configuration for warming operations."""
    settings = get_bff_settings()
    return {
        "requests_per_second": getattr(
            settings, "warming_requests_per_second", 2
        ),  ***REMOVED*** 2 RPS max
        "burst_size": getattr(
            settings, "warming_burst_size", 5
        ),  ***REMOVED*** Allow 5 request burst
        "backoff_base": getattr(
            settings, "warming_backoff_base", 2.0
        ),  ***REMOVED*** Exponential backoff base
        "backoff_max": getattr(
            settings, "warming_backoff_max", 30.0
        ),  ***REMOVED*** Max backoff 30s
        "jitter": getattr(settings, "warming_jitter", True),  ***REMOVED*** Add jitter to backoff
    }


class WarmingRateLimiter:
    """Rate limiter for cache warming operations to prevent 429 errors."""

    def __init__(self, requests_per_second: float = 2.0, burst_size: int = 5):
        """Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
            burst_size: Number of requests that can be made in a burst
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens: float = float(burst_size)  ***REMOVED*** Use float for token calculations
        self.last_update = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request (blocks if rate limited)."""
        async with self._lock:
            now = asyncio.get_event_loop().time()

            ***REMOVED*** Add tokens based on time elapsed
            time_passed = now - self.last_update
            self.tokens = min(
                float(self.burst_size),
                self.tokens + time_passed * self.requests_per_second,
            )
            self.last_update = now

            ***REMOVED*** If we don't have tokens, wait
            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.requests_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
            else:
                self.tokens -= 1.0


***REMOVED*** Global rate limiter instance
_global_warming_rate_limiter: WarmingRateLimiter | None = None


def get_warming_rate_limiter() -> WarmingRateLimiter:
    """Get the global warming rate limiter instance.

    Returns:
        Global warming rate limiter instance
    """
    global _global_warming_rate_limiter
    if _global_warming_rate_limiter is None:
        rate_limits = get_warming_rate_limits()
        _global_warming_rate_limiter = WarmingRateLimiter(
            requests_per_second=float(rate_limits["requests_per_second"]),
            burst_size=int(rate_limits["burst_size"]),
        )
    return _global_warming_rate_limiter


def get_bff_warming_settings() -> dict[str, Any]:
    """Get dict representation of BFF warming settings for JSON responses.

    Returns:
        Dictionary with warming configuration settings
    """
    settings = get_bff_settings()

    return {
        "max_concurrent_operations": getattr(
            settings,
            "warming_max_concurrent",
            3,  ***REMOVED*** Reduced for rate limiting
        ),
        "max_items_per_strategy": getattr(
            settings, "warming_max_items_per_strategy", 10000
        ),
        "operation_timeout_seconds": getattr(
            settings,
            "warming_operation_timeout",
            120,  ***REMOVED*** Increased timeout
        ),
        "enable_popular_content": True,
        "enable_user_specific": True,
        "enable_scheduled": True,
        "enable_metrics_driven": True,
        "rate_limits": get_warming_rate_limits(),
    }
