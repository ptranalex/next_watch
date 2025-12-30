"""Abstract base cache provider."""

import json
from abc import ABC, abstractmethod
from typing import cast

import structlog

from cache.types import TTL, CacheKey, CacheResult, CacheSetResult, JSONSerializable

logger = structlog.get_logger(__name__)


class CacheProvider(ABC):
    """Abstract base class for cache providers."""

    def __init__(self, key_prefix: str = "") -> None:
        """Initialize the cache provider.

        Args:
            key_prefix: Prefix to add to all cache keys
        """
        self.key_prefix = key_prefix
        self.logger = logger.bind(provider=self.__class__.__name__)

    def _build_key(self, key: CacheKey) -> str:
        """Build the full cache key with prefix.

        Args:
            key: The base cache key

        Returns:
            The full cache key with prefix
        """
        if self.key_prefix:
            return f"{self.key_prefix}:{key}"
        return key

    def _serialize_json(self, value: JSONSerializable) -> str:
        """Serialize a value to JSON string.

        Args:
            value: The value to serialize

        Returns:
            JSON string representation

        Raises:
            ValueError: If value is not JSON serializable
        """
        try:
            return json.dumps(value, separators=(",", ":"))
        except (TypeError, ValueError) as e:
            self.logger.error("Failed to serialize value to JSON", error=str(e))
            raise ValueError(f"Value is not JSON serializable: {e}") from e

    def _deserialize_json(self, value: str) -> JSONSerializable:
        """Deserialize a JSON string to Python object.

        Args:
            value: The JSON string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            ValueError: If value is not valid JSON
        """
        try:
            result = json.loads(value)
            # Cast to JSONSerializable since json.loads can return Any
            return cast(JSONSerializable, result)
        except (TypeError, ValueError) as e:
            self.logger.error("Failed to deserialize JSON value", error=str(e))
            raise ValueError(f"Invalid JSON value: {e}") from e

    @abstractmethod
    async def get_raw(self, key: CacheKey) -> str | None:
        """Get raw string value from cache.

        Args:
            key: The cache key

        Returns:
            The cached value as string, or None if not found
        """
        pass

    @abstractmethod
    async def set_raw(self, key: CacheKey, value: str, ttl: TTL = None) -> CacheSetResult:
        """Set raw string value in cache.

        Args:
            key: The cache key
            value: The value to cache as string
            ttl: Time to live in seconds, None for no expiration

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, key: CacheKey) -> bool:
        """Delete a key from cache.

        Args:
            key: The cache key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        pass

    @abstractmethod
    async def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in cache.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Perform a health check on the cache provider.

        Returns:
            True if healthy, False otherwise
        """
        pass

    # High-level JSON operations
    async def get_json(self, key: CacheKey) -> CacheResult:
        """Get JSON value from cache.

        Args:
            key: The cache key

        Returns:
            The cached value as Python object, or None if not found
        """
        raw_value = await self.get_raw(key)
        if raw_value is None:
            return None

        try:
            return self._deserialize_json(raw_value)
        except ValueError:
            # Log error but don't raise - treat as cache miss
            self.logger.warning("Found invalid JSON in cache, treating as miss", key=key)
            return None

    async def set_json(
        self, key: CacheKey, value: JSONSerializable, ttl: TTL = None
    ) -> CacheSetResult:
        """Set JSON value in cache.

        Args:
            key: The cache key
            value: The value to cache (must be JSON serializable)
            ttl: Time to live in seconds, None for no expiration

        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = self._serialize_json(value)
            return await self.set_raw(key, json_value, ttl)
        except ValueError:
            # Log error and return False
            self.logger.error("Failed to cache non-serializable value", key=key)
            return False

    async def delete_key(self, key: CacheKey) -> bool:
        """Delete a key from cache (alias for delete).

        Args:
            key: The cache key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        return await self.delete(key)

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.

        Args:
            pattern: The pattern to match keys against (e.g., "user:123:*")

        Returns:
            Number of keys deleted
        """
        pass
