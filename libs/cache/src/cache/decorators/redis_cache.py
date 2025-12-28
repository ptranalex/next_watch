"""Redis cache decorator for automatic function caching."""

import asyncio
import functools
import hashlib
import inspect
import json
import time
from collections.abc import Callable
from typing import Any, TypeVar

from ..manager import CacheManager
from ..metrics.collector import get_global_collector

F = TypeVar("F", bound=Callable[..., Any])


def redis_cache(
    ttl: int,
    key_builder: Callable[..., str] | None = None,
    key_prefix: str | None = None,
    cache_manager: CacheManager | None = None,
    enable_metrics: bool = True,
) -> Callable[[F], F]:
    """Decorator for automatic Redis caching of function results.

    Args:
        ttl: Time to live in seconds
        key_builder: Optional function to build cache key from function args
        key_prefix: Optional prefix for cache keys
        cache_manager: Optional cache manager instance (will create default if None)
        enable_metrics: Whether to collect performance metrics (default: True)

    Returns:
        Decorated function with automatic caching

    Example:
        @redis_cache(ttl=600, key_prefix="movie")
        async def get_movie_details(movie_id: int):
            return await expensive_operation(movie_id)

        ***REMOVED*** With custom key builder
        @redis_cache(
            ttl=600,
            key_builder=lambda movie_id, user_id=None: f"movie:{movie_id}:user:{user_id or 'anon'}"
        )
        async def get_movie_screen(movie_id: int, user_id: Optional[int] = None):
            return await expensive_aggregation(movie_id, user_id)
    """

    def decorator(func: F) -> F:
        ***REMOVED*** Get function signature for key building
        sig = inspect.signature(func)

        ***REMOVED*** Initialize cache manager if not provided
        _cache_manager = cache_manager or CacheManager.from_settings()

        ***REMOVED*** Get metrics collector if enabled
        _metrics_collector = get_global_collector() if enable_metrics else None

        def _build_cache_key(*args: Any, **kwargs: Any) -> str:
            """Build cache key from function arguments."""
            if key_builder:
                ***REMOVED*** Use custom key builder
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                return key_builder(**bound_args.arguments)
            else:
                ***REMOVED*** Auto-generate key from function name and arguments
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                ***REMOVED*** Create deterministic key from function name and arguments
                func_name = func.__name__
                args_str = json.dumps(bound_args.arguments, sort_keys=True, default=str)
                args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]

                base_key = f"{func_name}:{args_hash}"
                if key_prefix:
                    return f"{key_prefix}:{base_key}"
                return base_key

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                cache_key = _build_cache_key(*args, **kwargs)
                function_name = f"{func.__module__}.{func.__name__}"

                ***REMOVED*** Start timing
                start_time = time.perf_counter()

                ***REMOVED*** Try to get from cache first
                try:
                    cached_result = await _cache_manager.get_json(cache_key)
                    if cached_result is not None:
                        ***REMOVED*** Cache hit - record metrics
                        if _metrics_collector:
                            end_time = time.perf_counter()
                            duration_ms = (end_time - start_time) * 1000
                            _metrics_collector.record_cache_hit(function_name, duration_ms)
                        return cached_result
                except Exception:
                    ***REMOVED*** Cache read failed, continue to function execution
                    pass

                ***REMOVED*** Cache miss - execute function
                result = await func(*args, **kwargs)

                ***REMOVED*** Record cache miss metrics
                if _metrics_collector:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    _metrics_collector.record_cache_miss(function_name, duration_ms)

                ***REMOVED*** Cache the result
                try:
                    await _cache_manager.set_json(cache_key, result, ttl=ttl)
                except Exception:
                    ***REMOVED*** Cache write failed, but return result anyway
                    pass

                return result

            return async_wrapper  ***REMOVED*** type: ignore
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                ***REMOVED*** For sync functions, we need to handle async cache operations
                ***REMOVED*** This is a simplified implementation - in practice you might want
                ***REMOVED*** to use a sync Redis client or run in thread pool
                raise NotImplementedError(
                    "Synchronous function caching not yet implemented. "
                    "Please use async functions with @redis_cache decorator."
                )

            return sync_wrapper  ***REMOVED*** type: ignore

    return decorator
