"""Cache configuration settings."""

import os
from typing import Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class CacheSettings(BaseSettings):
    """Configuration settings for the cache library."""

    ***REMOVED*** Redis connection settings
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_pool_size: int = Field(default=10, description="Redis connection pool size")
    redis_timeout: int = Field(
        default=5, description="Redis connection timeout in seconds"
    )

    ***REMOVED*** Cache behavior settings
    key_prefix: str = Field(
        default="nextwatch", description="Global key prefix for all cache keys"
    )
    enable_metrics: bool = Field(
        default=True, description="Enable cache metrics collection"
    )

    ***REMOVED*** Domain-specific TTL settings (in seconds)
    ttl_movie_data: int = Field(
        default=600, description="TTL for movie data cache"
    )  ***REMOVED*** 10 minutes
    ttl_user_session: int = Field(
        default=3600, description="TTL for user session cache"
    )  ***REMOVED*** 1 hour
    ttl_popular_content: int = Field(
        default=1800, description="TTL for popular content cache"  ***REMOVED*** 30 minutes
    )
    cache_ttl_default: int = Field(
        default=300, description="Default TTL when not specified"
    )  ***REMOVED*** 5 minutes

    class Config:
        """Pydantic configuration."""

        env_prefix = "CACHE_"
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  ***REMOVED*** Ignore extra fields for compatibility

    def get_redis_url(self) -> str:
        """Get the Redis URL, with environment variable override.

        Checks for CACHE_REDIS_URL only, then uses the configured redis_url value.
        No fallback to REDIS_URL to ensure consistent configuration.
        """
        return os.getenv("CACHE_REDIS_URL", self.redis_url)

    def validate_config(self) -> List[str]:
        """Validate the cache configuration.

        Checks that Redis configuration is using the proper CACHE_ prefixed environment variables.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Check if non-prefixed Redis environment variables are being used
        legacy_vars = {
            "REDIS_URL": "CACHE_REDIS_URL",
            "REDIS_MAX_CONNECTIONS": "CACHE_REDIS_MAX_CONNECTIONS",
            "REDIS_SOCKET_TIMEOUT": "CACHE_REDIS_SOCKET_TIMEOUT",
            "REDIS_RETRY_ON_TIMEOUT": "CACHE_REDIS_RETRY_ON_TIMEOUT",
        }

        for old_var, new_var in legacy_vars.items():
            if os.getenv(old_var) is not None and os.getenv(new_var) is None:
                issues.append(
                    f"Found {old_var} but {new_var} is not set. Use {new_var} instead."
                )

        ***REMOVED*** Check if Redis URL is set properly
        if os.getenv("CACHE_REDIS_URL") is None and "localhost" in self.redis_url:
            issues.append(
                f"CACHE_REDIS_URL is not set, using default: {self.redis_url}"
            )

        return issues

    def get_ttl_for_domain(self, domain: str) -> int:
        """Get TTL for a specific domain, falling back to default."""
        domain_ttl_map = {
            "movie": self.ttl_movie_data,
            "user": self.ttl_user_session,
            "popular": self.ttl_popular_content,
        }
        return domain_ttl_map.get(domain, self.cache_ttl_default)
