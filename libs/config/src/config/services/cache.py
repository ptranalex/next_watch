"""Cache configuration mixin for Redis connections.

Provides configuration for Redis cache connections with straightforward settings
and validation.
"""

from typing import Any
from urllib.parse import urlparse

from pydantic import Field, validator


class CacheConfigMixin:
    """Redis cache configuration mixin with simplified approach.

    This mixin provides Redis cache connection configuration that can be composed
    into service configurations. It includes connection settings and cache TTLs
    with a straightforward approach.

    Environment variables (with service prefix):
    - {SERVICE}_REDIS_URL: Redis connection URL
    - {SERVICE}_REDIS_MAX_CONNECTIONS: Maximum connections in pool
    - {SERVICE}_REDIS_SOCKET_TIMEOUT: Socket timeout in seconds
    - {SERVICE}_CACHE_TTL_DEFAULT: Default cache TTL in seconds
    - {SERVICE}_CACHE_KEY_PREFIX: Prefix for cache keys
    """

    ***REMOVED*** Redis connection settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_max_connections: int = Field(
        default=10, description="Maximum number of connections in the Redis pool"
    )
    redis_socket_timeout: int = Field(default=30, description="Socket timeout in seconds")
    redis_socket_connect_timeout: int = Field(
        default=5, description="Socket connection timeout in seconds"
    )
    redis_retry_on_timeout: bool = Field(default=True, description="Retry operations on timeout")

    ***REMOVED*** Cache-specific settings
    cache_ttl_default: int = Field(
        default=300, description="Default cache TTL in seconds (5 minutes)"
    )
    cache_key_prefix: str = Field(default="", description="Prefix for all cache keys")
    cache_ttl_short: int = Field(default=60, description="Short cache TTL in seconds (1 minute)")
    cache_ttl_medium: int = Field(
        default=900, description="Medium cache TTL in seconds (15 minutes)"
    )
    cache_ttl_long: int = Field(default=3600, description="Long cache TTL in seconds (1 hour)")

    @validator("redis_url")
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format and scheme."""
        if not v:
            raise ValueError("Redis URL cannot be empty")

        try:
            parsed = urlparse(v)
            if parsed.scheme not in ["redis", "rediss"]:
                raise ValueError(
                    f"Unsupported Redis scheme: {parsed.scheme}. "
                    "Only 'redis' and 'rediss' (SSL) are supported"
                )

            if not parsed.hostname:
                raise ValueError("Redis URL must include hostname")

            ***REMOVED*** Validate database number if present
            if parsed.path and parsed.path != "/":
                try:
                    db_num = int(parsed.path.lstrip("/"))
                    if db_num < 0 or db_num > 15:
                        raise ValueError("Redis database number must be between 0-15")
                except ValueError:
                    raise ValueError("Invalid Redis database number in URL")

        except Exception as e:
            raise ValueError(f"Invalid Redis URL format: {e}")

        return v

    @validator("redis_max_connections")
    def validate_max_connections(cls, v: int) -> int:
        """Validate max connections is positive."""
        if v < 1:
            raise ValueError("Redis max connections must be at least 1")
        if v > 100:
            raise ValueError("Redis max connections should not exceed 100")
        return v

    @validator("redis_socket_timeout", "redis_socket_connect_timeout")
    def validate_timeouts(cls, v: int) -> int:
        """Validate timeouts are positive."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Timeout should not exceed 300 seconds")
        return v

    @validator("cache_ttl_default", "cache_ttl_short", "cache_ttl_medium", "cache_ttl_long")
    def validate_cache_ttl(cls, v: int) -> int:
        """Validate cache TTL is positive."""
        if v < 1:
            raise ValueError("Cache TTL must be at least 1 second")
        if v > 86400:  ***REMOVED*** 24 hours
            raise ValueError("Cache TTL should not exceed 24 hours")
        return v

    @validator("cache_key_prefix")
    def validate_cache_key_prefix(cls, v: str) -> str:
        """Validate cache key prefix format."""
        if v and not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Cache key prefix must contain only alphanumeric, underscore, or dash characters"
            )
        return v

    def get_redis_config(self) -> dict[str, Any]:
        """Get Redis connection configuration dictionary.

        Returns:
            Dictionary with Redis connection configuration
        """
        return {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
            "socket_timeout": self.redis_socket_timeout,
            "socket_connect_timeout": self.redis_socket_connect_timeout,
            "retry_on_timeout": self.redis_retry_on_timeout,
        }

    def get_cache_config(self) -> dict[str, Any]:
        """Get cache configuration dictionary.

        Returns:
            Dictionary with cache-specific configuration
        """
        return {
            "default_ttl": self.cache_ttl_default,
            "key_prefix": self.cache_key_prefix,
            "ttl_presets": {
                "short": self.cache_ttl_short,
                "medium": self.cache_ttl_medium,
                "long": self.cache_ttl_long,
            },
        }

    def get_redis_url_masked(self) -> str:
        """Get Redis URL with credentials masked for logging.

        Returns:
            Redis URL with password masked
        """
        try:
            parsed = urlparse(self.redis_url)
            if parsed.password:
                masked_url = self.redis_url.replace(f":{parsed.password}@", ":***@")
                return masked_url
            return self.redis_url
        except Exception:
            return "***"

    def format_cache_key(self, key: str, namespace: str | None = None) -> str:
        """Format a cache key with prefix and optional namespace.

        Args:
            key: Base cache key
            namespace: Optional namespace for the key

        Returns:
            Formatted cache key with prefix and namespace
        """
        if namespace:
            return f"{self.cache_key_prefix}{namespace}:{key}"
        return f"{self.cache_key_prefix}{key}"

    def validate_cache_production_settings(self) -> list[str]:
        """Validate cache configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        if (
            self.redis_url.startswith("redis://localhost")
            and hasattr(self, "is_production")
            and getattr(self, "is_production")
        ):
            issues.append("Redis URL should not use localhost in production")

        return issues

    def log_cache_configuration(self) -> None:
        """Log cache configuration with reduced verbosity."""
        if hasattr(self, "debug") and (
            getattr(self, "debug") or getattr(self, "log_level", "INFO") == "DEBUG"
        ):
            from config.logging import get_logger

            logger = get_logger(__name__)

            ***REMOVED*** Log Redis URL (masked) only in debug mode
            logger.debug(f"Redis: {self.get_redis_url_masked()}")

            ***REMOVED*** Log cache TTL settings in compact format
            logger.debug(
                f"Cache TTLs: default={self.cache_ttl_default}s, "
                + f"short={self.cache_ttl_short}s, "
                + f"medium={self.cache_ttl_medium}s, "
                + f"long={self.cache_ttl_long}s"
            )
