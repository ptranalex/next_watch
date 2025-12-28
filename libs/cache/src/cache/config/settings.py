"""Cache configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class CacheSettings(BaseSettings):
    """Configuration settings for the cache library.

    Uses standardized environment variable names that all services can share.
    No prefixes - keeps it simple and consistent across the monorepo.
    """

    ***REMOVED*** Redis connection settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_max_connections: int = Field(default=10, description="Redis connection pool size")
    redis_socket_timeout: int = Field(default=5, description="Redis connection timeout in seconds")

    ***REMOVED*** Cache behavior settings
    cache_key_prefix: str = Field(
        default="nextwatch", description="Global key prefix for all cache keys"
    )
    cache_enable_metrics: bool = Field(default=True, description="Enable cache metrics collection")

    ***REMOVED*** TTL settings (in seconds)
    cache_ttl_default: int = Field(
        default=300, description="Default TTL when not specified"
    )  ***REMOVED*** 5 minutes
    cache_ttl_short: int = Field(
        default=60, description="Short TTL for frequently changing data"
    )  ***REMOVED*** 1 minute
    cache_ttl_medium: int = Field(
        default=900, description="Medium TTL for moderately stable data"
    )  ***REMOVED*** 15 minutes
    cache_ttl_long: int = Field(default=3600, description="Long TTL for stable data")  ***REMOVED*** 1 hour

    class Config:
        """Pydantic configuration."""

        env_prefix = ""  ***REMOVED*** No prefix - standardized variable names
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  ***REMOVED*** Ignore extra fields for compatibility

    def get_ttl_for_domain(self, domain: str) -> int:
        """Get TTL for a specific domain, falling back to default."""
        domain_ttl_map = {
            "movie": self.cache_ttl_medium,  ***REMOVED*** 15 minutes
            "user": self.cache_ttl_long,  ***REMOVED*** 1 hour
            "popular": self.cache_ttl_short,  ***REMOVED*** 1 minute
        }
        return domain_ttl_map.get(domain, self.cache_ttl_default)
