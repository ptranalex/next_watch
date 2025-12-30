"""Smart Cache Warming Service.

This module provides intelligent, event-driven cache warming that operates
within FastAPI services without the security and performance issues of
manual API-triggered bulk warming.
"""

import asyncio
import logging
import random
import time
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    try:
        from config.logging import get_logger
    except ImportError:

        def get_logger(name: str) -> logging.Logger:
            return logging.getLogger(name)

else:
    try:
        from config.logging import get_logger
    except ImportError:

        def get_logger(name: str) -> logging.Logger:
            return logging.getLogger(name)


logger = get_logger(__name__)


class TokenBucketLimiter:
    """Token bucket rate limiter for smart warming operations."""

    def __init__(self, rate: float = 5.0, burst: int = 10):
        """Initialize token bucket limiter.

        Args:
            rate: Tokens per second
            burst: Burst capacity
        """
        self.rate = rate
        self.burst = burst
        self.tokens: float = float(burst)
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Try to acquire a token.

        Returns:
            True if token acquired, False if rate limited
        """
        async with self._lock:
            now = time.time()

            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now

            # Check if we have tokens available
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True

            return False


class SmartWarmingService:
    """Intelligent, event-driven cache warming service.

    This service provides smart warming capabilities that:
    - React to user behavior patterns
    - Warm related content on cache misses
    - Rate limit to prevent downstream service overload
    - Integrate seamlessly with FastAPI background tasks
    """

    def __init__(
        self,
        rate_limit_rps: float = 5.0,
        burst_size: int = 10,
        warming_enabled: bool = True,
    ):
        """Initialize smart warming service.

        Args:
            rate_limit_rps: Rate limit for warming operations (requests per second)
            burst_size: Burst capacity for token bucket
            warming_enabled: Whether warming is enabled (for testing/debugging)
        """
        self.rate_limiter = TokenBucketLimiter(rate_limit_rps, burst_size)
        self.warming_enabled = warming_enabled
        self.warming_stats = {
            "operations_attempted": 0,
            "operations_successful": 0,
            "operations_rate_limited": 0,
            "operations_failed": 0,
            "last_operation": None,
        }

        logger.info(
            "Smart warming service initialized",
            rate_limit_rps=rate_limit_rps,
            burst_size=burst_size,
            enabled=warming_enabled,
        )

    async def warm_on_cache_miss(
        self,
        cache_key: str,
        context: dict[str, Any],
        warming_func: Callable[[], Awaitable[Any]] | None = None,
    ) -> bool:
        """Warm related content when a cache miss is detected.

        Args:
            cache_key: The cache key that missed
            context: Context about the miss (user_id, resource_type, etc.)
            warming_func: Optional specific warming function to call

        Returns:
            True if warming was attempted, False if rate limited or disabled
        """
        if not self.warming_enabled:
            return False

        self.warming_stats["operations_attempted"] += 1

        # Check rate limiting
        if not await self.rate_limiter.acquire():
            self.warming_stats["operations_rate_limited"] += 1
            logger.debug(
                "Smart warming rate limited",
                cache_key=cache_key,
                context=context,
            )
            return False

        try:
            logger.info(
                "Smart warming triggered by cache miss",
                cache_key=cache_key,
                context=context,
            )

            # Execute warming function if provided
            if warming_func:
                await warming_func()
            else:
                # Default warming logic based on context
                await self._warm_related_content(cache_key, context)

            self.warming_stats["operations_successful"] += 1
            self.warming_stats["last_operation"] = datetime.utcnow().isoformat()

            logger.info(
                "Smart warming completed successfully",
                cache_key=cache_key,
                context=context,
            )

            return True

        except Exception as e:
            self.warming_stats["operations_failed"] += 1
            logger.warning(
                "Smart warming failed",
                cache_key=cache_key,
                context=context,
                error=str(e),
            )
            return False

    async def warm_from_trigger(
        self,
        trigger_name: str,
        warming_func: Callable[[], Awaitable[Any]] | None = None,
        **context: Any,
    ) -> bool:
        """Warm cache based on any trigger event.

        Args:
            trigger_name: Name of the trigger event (generic identifier)
            warming_func: Business-specific warming function to execute
            **context: Additional context for the warming function

        Returns:
            True if warming was attempted, False if rate limited or disabled
        """
        if not self.warming_enabled:
            return False

        self.warming_stats["operations_attempted"] += 1

        # Check rate limiting
        if not await self.rate_limiter.acquire():
            self.warming_stats["operations_rate_limited"] += 1
            logger.debug(
                "Smart warming rate limited for trigger",
                trigger=trigger_name,
                context=context,
            )
            return False

        try:
            logger.info(
                "Smart warming triggered",
                trigger=trigger_name,
                context=context,
            )

            # Execute the provided warming function
            if warming_func:
                await warming_func()
            else:
                logger.debug(f"No warming function provided for trigger: {trigger_name}")

            self.warming_stats["operations_successful"] += 1
            self.warming_stats["last_operation"] = datetime.utcnow().isoformat()

            return True

        except Exception as e:
            self.warming_stats["operations_failed"] += 1
            logger.warning(
                "Smart warming failed for trigger",
                trigger=trigger_name,
                context=context,
                error=str(e),
            )
            return False

    async def warm_popular_content(
        self, warming_func: Callable[[], Awaitable[Any]], limit: int = 10
    ) -> bool:
        """Warm popular content (small scale).

        Args:
            warming_func: Business-specific function to execute the warming
            limit: Maximum number of items to warm

        Returns:
            True if warming was attempted, False if rate limited or disabled
        """
        return await self.warm_from_trigger("popular_content_refresh", warming_func, limit=limit)

    def get_stats(self) -> dict[str, Any]:
        """Get warming statistics.

        Returns:
            Dictionary with warming statistics
        """
        return {
            **self.warming_stats,
            "rate_limiter": {
                "rate": self.rate_limiter.rate,
                "burst": self.rate_limiter.burst,
                "current_tokens": self.rate_limiter.tokens,
            },
            "enabled": self.warming_enabled,
        }

    def reset_stats(self) -> None:
        """Reset warming statistics."""
        self.warming_stats = {
            "operations_attempted": 0,
            "operations_successful": 0,
            "operations_rate_limited": 0,
            "operations_failed": 0,
            "last_operation": None,
        }

    async def _warm_related_content(self, cache_key: str, context: dict[str, Any]) -> None:
        """Default warming logic for cache misses.

        This is a fallback that should be overridden by business logic.
        """
        logger.debug(
            "Generic warming fallback triggered",
            cache_key=cache_key,
            context=context,
        )

        # Small delay to prevent overwhelming downstream services
        await asyncio.sleep(random.uniform(0.1, 0.5))


# Global smart warming service instance
_global_smart_warming_service: SmartWarmingService | None = None


def get_smart_warming_service() -> SmartWarmingService:
    """Get the global smart warming service instance.

    Returns:
        Global smart warming service instance
    """
    global _global_smart_warming_service
    if _global_smart_warming_service is None:
        _global_smart_warming_service = SmartWarmingService()
    return _global_smart_warming_service


def configure_smart_warming(
    rate_limit_rps: float = 5.0, burst_size: int = 10, warming_enabled: bool = True
) -> SmartWarmingService:
    """Configure the global smart warming service.

    Args:
        rate_limit_rps: Rate limit for warming operations
        burst_size: Burst capacity for token bucket
        warming_enabled: Whether warming is enabled

    Returns:
        Configured smart warming service
    """
    global _global_smart_warming_service
    _global_smart_warming_service = SmartWarmingService(
        rate_limit_rps=rate_limit_rps,
        burst_size=burst_size,
        warming_enabled=warming_enabled,
    )
    return _global_smart_warming_service
