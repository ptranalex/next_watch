"""Redis cache provider implementation."""

from typing import Any, Optional, Union

import redis.asyncio as redis
import structlog

from cache.config.settings import CacheSettings
from cache.providers.base import CacheProvider
from cache.types import CacheKey, CacheSetResult, TTL

logger = structlog.get_logger(__name__)


class RedisProvider(CacheProvider):
    """Redis-based cache provider with connection pooling."""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        pool_size: int = 10,
        timeout: int = 5,
        key_prefix: str = "",
        **redis_kwargs: Any,
    ) -> None:
        """Initialize Redis cache provider.

        Args:
            redis_url: Redis connection URL
            pool_size: Connection pool size
            timeout: Connection timeout in seconds
            key_prefix: Prefix for all cache keys
            **redis_kwargs: Additional Redis connection parameters
        """
        super().__init__(key_prefix=key_prefix)

        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.pool_size = pool_size
        self.timeout = timeout
        self.redis_kwargs = redis_kwargs

        ***REMOVED*** Connection pool will be initialized lazily
        self._pool: Optional[redis.ConnectionPool] = None  ***REMOVED*** type: ignore
        self._client: Optional[redis.Redis] = None  ***REMOVED*** type: ignore

        self.logger = logger.bind(
            provider="RedisProvider",
            redis_url=self._mask_url(self.redis_url),
            pool_size=pool_size,
        )

    @classmethod
    def from_settings(cls, settings: CacheSettings) -> "RedisProvider":
        """Create Redis provider from cache settings.

        Args:
            settings: Cache configuration settings

        Returns:
            Configured Redis provider instance
        """
        return cls(
            redis_url=settings.redis_url,
            pool_size=settings.redis_max_connections,
            timeout=settings.redis_socket_timeout,
            key_prefix=settings.cache_key_prefix,
        )

    def _mask_url(self, url: str) -> str:
        """Mask sensitive information in Redis URL for logging.

        Args:
            url: Redis URL

        Returns:
            Masked URL safe for logging
        """
        if "@" in url:
            ***REMOVED*** Mask password in URL like redis://user:password@host:port/db
            parts = url.split("@")
            if len(parts) == 2:
                auth_part = parts[0]
                if ":" in auth_part:
                    scheme_user = auth_part.rsplit(":", 1)[0]
                    return f"{scheme_user}:***@{parts[1]}"
        return url

    async def _get_client(self) -> redis.Redis:  ***REMOVED*** type: ignore
        """Get Redis client, initializing connection pool if needed.

        Returns:
            Redis client instance
        """
        if self._client is None:
            self.logger.debug("Initializing Redis connection pool")

            self._pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.pool_size,
                socket_timeout=self.timeout,
                socket_connect_timeout=self.timeout,
                retry_on_timeout=True,
                **self.redis_kwargs,
            )

            self._client = redis.Redis(
                connection_pool=self._pool,
                decode_responses=True,  ***REMOVED*** Automatically decode bytes to strings
            )

            self.logger.info("Redis connection pool initialized")

        return self._client

    async def get_raw(self, key: CacheKey) -> Optional[str]:
        """Get raw string value from Redis.

        Args:
            key: The cache key

        Returns:
            The cached value as string, or None if not found
        """
        full_key = self._build_key(key)

        try:
            client = await self._get_client()
            value = await client.get(full_key)

            if value is not None:
                self.logger.debug(
                    "Cache hit",
                    key=key,
                    full_key=full_key,
                    value_type=type(value).__name__,
                    value_len=len(str(value)),
                )
                ***REMOVED*** Handle both string and bytes responses
                if isinstance(value, bytes):
                    return value.decode("utf-8")
                return str(value)
            else:
                self.logger.debug("Cache miss", key=key, full_key=full_key)
                return None

        except Exception as e:
            self.logger.error("Failed to get value from Redis", key=key, error=str(e))
            ***REMOVED*** Return None on error to treat as cache miss
            return None

    async def set_raw(
        self, key: CacheKey, value: str, ttl: TTL = None
    ) -> CacheSetResult:
        """Set raw string value in Redis.

        Args:
            key: The cache key
            value: The value to cache as string
            ttl: Time to live in seconds, None for no expiration

        Returns:
            True if successful, False otherwise
        """
        full_key = self._build_key(key)

        try:
            client = await self._get_client()

            result: Union[bool, None]
            if ttl is not None:
                result = await client.setex(full_key, ttl, value)
            else:
                result = await client.set(full_key, value)

            success = bool(result) if result is not None else False
            if success:
                self.logger.debug("Cache set", key=key, full_key=full_key, ttl=ttl)
            else:
                self.logger.warning("Cache set failed", key=key, full_key=full_key)

            return success

        except Exception as e:
            self.logger.error("Failed to set value in Redis", key=key, error=str(e))
            return False

    async def delete(self, key: CacheKey) -> bool:
        """Delete a key from Redis.

        Args:
            key: The cache key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        full_key = self._build_key(key)

        try:
            client = await self._get_client()
            result = await client.delete(full_key)

            deleted = result > 0
            if deleted:
                self.logger.debug("Cache delete", key=key, full_key=full_key)
            else:
                self.logger.debug(
                    "Cache delete - key not found", key=key, full_key=full_key
                )

            return deleted

        except Exception as e:
            self.logger.error("Failed to delete key from Redis", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.

        Uses Redis SCAN + MATCH + DELETE for efficient pattern-based deletion.

        Args:
            pattern: The pattern to match keys against (e.g., "user:123:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = await self._get_client()

            ***REMOVED*** Apply key prefix if configured
            full_pattern = self._build_key(pattern)

            ***REMOVED*** Use scan_iter to efficiently iterate through matching keys
            deleted_count = 0
            batch_size = 100
            keys_to_delete = []

            self.logger.debug(
                "Scanning for keys matching pattern",
                pattern=pattern,
                full_pattern=full_pattern,
            )

            ***REMOVED*** Iterate through matching keys
            async for key in client.scan_iter(match=full_pattern, count=batch_size):
                keys_to_delete.append(key)

                ***REMOVED*** Delete in batches for efficiency
                if len(keys_to_delete) >= batch_size:
                    if keys_to_delete:
                        result = await client.delete(*keys_to_delete)
                        deleted_count += result
                        self.logger.debug(
                            "Deleted batch of keys", count=result, total=deleted_count
                        )
                    keys_to_delete = []

            ***REMOVED*** Delete any remaining keys
            if keys_to_delete:
                result = await client.delete(*keys_to_delete)
                deleted_count += result
                self.logger.debug(
                    "Deleted final batch of keys", count=result, total=deleted_count
                )

            self.logger.info(
                "Pattern-based key deletion complete",
                pattern=pattern,
                deleted_count=deleted_count,
            )
            return deleted_count

        except Exception as e:
            self.logger.error(
                "Failed to delete keys by pattern", pattern=pattern, error=str(e)
            )
            return 0

    async def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in Redis.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """
        full_key = self._build_key(key)

        try:
            client = await self._get_client()
            result = await client.exists(full_key)

            exists = result > 0
            self.logger.debug(
                "Cache exists check", key=key, full_key=full_key, exists=exists
            )
            return exists

        except Exception as e:
            self.logger.error(
                "Failed to check key existence in Redis", key=key, error=str(e)
            )
            return False

    async def health_check(self) -> bool:
        """Perform a health check on Redis connection.

        Returns:
            True if healthy, False otherwise
        """
        try:
            client = await self._get_client()
            ***REMOVED*** Use PING command to check connection
            result = await client.ping()

            healthy = result is True
            if healthy:
                self.logger.debug("Redis health check passed")
            else:
                self.logger.warning(
                    "Redis health check failed - ping returned", result=result
                )

            return healthy

        except Exception as e:
            self.logger.error("Redis health check failed", error=str(e))
            return False

    async def close(self) -> None:
        """Close Redis connection pool.

        Should be called when shutting down the application.
        """
        if self._client is not None:
            self.logger.info("Closing Redis connection pool")
            await self._client.close()
            self._client = None

        if self._pool is not None:
            await self._pool.disconnect()
            self._pool = None

    async def __aenter__(self) -> "RedisProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Async context manager exit."""
        await self.close()
