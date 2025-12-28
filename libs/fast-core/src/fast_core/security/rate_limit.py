"""Rate limiting utilities for FastAPI applications.

This module provides rate limiting functionality with multiple backends
including in-memory and Redis-based rate limiters.
"""

import time
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from config.logging import get_logger
from fastapi import HTTPException, Request

logger = get_logger(__name__)


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    async def is_rate_limited(self, key: str, identifier: str) -> bool:
        """Check if a request should be rate limited.

        Args:
            key: Rate limit key (e.g., 'login', 'api_call')
            identifier: Client identifier (e.g., IP address, user ID)

        Returns:
            True if request should be rate limited, False otherwise
        """
        pass

    @abstractmethod
    async def get_remaining_requests(self, key: str, identifier: str) -> int:
        """Get remaining requests for the current window.

        Args:
            key: Rate limit key
            identifier: Client identifier

        Returns:
            Number of remaining requests
        """
        pass

    @abstractmethod
    async def reset_limits(self, key: str, identifier: str) -> None:
        """Reset rate limits for a specific key and identifier.

        Args:
            key: Rate limit key
            identifier: Client identifier
        """
        pass


class MemoryRateLimiter(RateLimiter):
    """In-memory rate limiter using sliding window."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        window_size: int = 60,
    ):
        """Initialize memory rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            window_size: Window size in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.requests: dict[str, list] = {}

    async def is_rate_limited(self, key: str, identifier: str) -> bool:
        """Check if request is rate limited."""
        full_key = f"{key}:{identifier}"
        now = time.time()

        ***REMOVED*** Initialize if not exists
        if full_key not in self.requests:
            self.requests[full_key] = []

        ***REMOVED*** Clean old requests
        self.requests[full_key] = [
            req_time for req_time in self.requests[full_key] if now - req_time < self.window_size
        ]

        ***REMOVED*** Check if rate limited
        if len(self.requests[full_key]) >= self.requests_per_minute:
            return True

        ***REMOVED*** Add current request
        self.requests[full_key].append(now)
        return False

    async def get_remaining_requests(self, key: str, identifier: str) -> int:
        """Get remaining requests."""
        full_key = f"{key}:{identifier}"
        now = time.time()

        if full_key not in self.requests:
            return self.requests_per_minute

        ***REMOVED*** Clean old requests
        self.requests[full_key] = [
            req_time for req_time in self.requests[full_key] if now - req_time < self.window_size
        ]

        return max(0, self.requests_per_minute - len(self.requests[full_key]))

    async def reset_limits(self, key: str, identifier: str) -> None:
        """Reset rate limits."""
        full_key = f"{key}:{identifier}"
        if full_key in self.requests:
            del self.requests[full_key]


class RedisRateLimiter(RateLimiter):
    """Redis-based rate limiter."""

    def __init__(
        self,
        redis_client: Any,
        requests_per_minute: int = 60,
        window_size: int = 60,
    ):
        """Initialize Redis rate limiter.

        Args:
            redis_client: Redis client instance
            requests_per_minute: Maximum requests per minute
            window_size: Window size in seconds
        """
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size

    async def is_rate_limited(self, key: str, identifier: str) -> bool:
        """Check if request is rate limited using Redis."""
        full_key = f"rate_limit:{key}:{identifier}"
        now = time.time()

        try:
            ***REMOVED*** Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()

            ***REMOVED*** Remove old entries
            pipe.zremrangebyscore(full_key, 0, now - self.window_size)

            ***REMOVED*** Count current entries
            pipe.zcard(full_key)

            ***REMOVED*** Add current request
            pipe.zadd(full_key, {str(now): now})

            ***REMOVED*** Set expiration
            pipe.expire(full_key, self.window_size)

            results = await pipe.execute()
            current_count = int(results[1])

            return current_count >= self.requests_per_minute

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            ***REMOVED*** Fail open - allow request if Redis is down
            return False

    async def get_remaining_requests(self, key: str, identifier: str) -> int:
        """Get remaining requests using Redis."""
        full_key = f"rate_limit:{key}:{identifier}"
        now = time.time()

        try:
            ***REMOVED*** Remove old entries and count
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(full_key, 0, now - self.window_size)
            pipe.zcard(full_key)

            results = await pipe.execute()
            current_count = int(results[1])

            return max(0, self.requests_per_minute - current_count)

        except Exception as e:
            logger.error(f"Redis remaining requests check failed: {e}")
            return self.requests_per_minute

    async def reset_limits(self, key: str, identifier: str) -> None:
        """Reset rate limits in Redis."""
        full_key = f"rate_limit:{key}:{identifier}"
        try:
            await self.redis.delete(full_key)
        except Exception as e:
            logger.error(f"Redis rate limit reset failed: {e}")


def get_client_key(request: Request) -> str:
    """Extract client identifier from request.

    Args:
        request: FastAPI request object

    Returns:
        Client identifier (IP address or forwarded IP)
    """
    ***REMOVED*** Check for forwarded IP first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ***REMOVED*** Take the first IP in case of multiple
        return forwarded_for.split(",")[0].strip()

    ***REMOVED*** Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    ***REMOVED*** Fall back to client IP
    if request.client:
        return request.client.host

    return "unknown"


async def check_rate_limit(
    request: Request,
    rate_limiter: RateLimiter,
    key: str = "default",
    requests: int = 60,
    window: int = 60,
) -> None:
    """Check rate limit and raise exception if exceeded.

    Args:
        request: FastAPI request object
        rate_limiter: Rate limiter instance
        key: Rate limit key
        requests: Maximum requests (for error message)
        window: Window size in seconds (for error message)

    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_key = get_client_key(request)

    if await rate_limiter.is_rate_limited(key, client_key):
        remaining = await rate_limiter.get_remaining_requests(key, client_key)

        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {requests} requests per {window} seconds.",
            headers={
                "X-RateLimit-Limit": str(requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + window)),
                "Retry-After": str(window),
            },
        )


def rate_limit(
    requests: int = 60,
    window: int = 60,
    key: str | None = None,
    rate_limiter: RateLimiter | None = None,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for rate limiting endpoints.

    Args:
        requests: Maximum requests per window
        window: Window size in seconds
        key: Custom rate limit key (defaults to endpoint name)
        rate_limiter: Custom rate limiter (defaults to memory rate limiter)

    Returns:
        Decorator function
    """
    if rate_limiter is None:
        rate_limiter = MemoryRateLimiter(
            requests_per_minute=requests,
            window_size=window,
        )

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ***REMOVED*** Find request object in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break

            if request:
                limit_key = key or func.__name__
                await check_rate_limit(
                    request=request,
                    rate_limiter=rate_limiter,
                    key=limit_key,
                    requests=requests,
                    window=window,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def create_redis_rate_limiter(
    redis_client: Any,
    requests_per_minute: int = 60,
    window_size: int = 60,
) -> RedisRateLimiter:
    """Create a Redis rate limiter instance.

    Args:
        redis_client: Redis client instance
        requests_per_minute: Maximum requests per minute
        window_size: Window size in seconds

    Returns:
        RedisRateLimiter instance
    """
    return RedisRateLimiter(
        redis_client=redis_client,
        requests_per_minute=requests_per_minute,
        window_size=window_size,
    )
