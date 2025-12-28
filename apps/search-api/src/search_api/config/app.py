"""Search API service configuration.

Provides configuration for the Search API service using the simplified config library.
"""

from typing import Any

from config.base.config import ServiceConfig
from config.logging import get_logger
from config.services.cache import CacheConfigMixin
from config.services.monitoring import MonitoringConfigMixin
from pydantic import Field, validator

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)


class SearchAPIConfig(ServiceConfig, CacheConfigMixin, MonitoringConfigMixin):
    """Search API service configuration.

    Provides configuration for the Search API service with cache and monitoring support.
    """

    ***REMOVED*** Service identification
    service_name: str = Field(default="search-api", description="Service name")
    port: int = Field(default=8004, description="Service port")

    ***REMOVED*** Logging configuration
    logs_dir: str | None = Field(
        default=None, description="Directory for log files (None disables file logging)"
    )

    ***REMOVED*** Backend service URLs
    backend_api_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    ml_api_url: str | None = Field(default=None, description="ML API URL (optional)")

    ***REMOVED*** Service timeouts
    backend_api_timeout: int = Field(default=30, description="Backend API timeout in seconds")
    ml_api_timeout: int = Field(default=60, description="ML API timeout in seconds")

    ***REMOVED*** Service-to-service authentication
    internal_api_key: str = Field(
        default="search-to-backend-secret-key",
        description="API key for service-to-service authentication",
    )

    ***REMOVED*** Search-specific settings
    max_suggestions: int = Field(default=50, description="Maximum number of suggestions to return")
    search_cache_ttl: int = Field(default=300, description="Search results cache TTL in seconds")
    suggestion_cache_ttl: int = Field(default=3600, description="Suggestion cache TTL in seconds")
    min_query_length: int = Field(default=1, description="Minimum query length for suggestions")
    max_query_length: int = Field(default=100, description="Maximum query length for search")

    ***REMOVED*** Redis-specific search settings
    redis_suggestion_key_prefix: str = Field(
        default="suggestions:", description="Redis key prefix for suggestions"
    )
    redis_entity_key_prefix: str = Field(
        default="entity:", description="Redis key prefix for entities"
    )
    redis_search_result_prefix: str = Field(
        default="search_results:", description="Redis key prefix for search results"
    )

    ***REMOVED*** Substring scan tuning
    suggestion_substring_min_len: int = Field(
        default=3, description="Minimum length to trigger substring scan"
    )
    suggestion_substring_budget_ms: int = Field(
        default=150, description="Time budget in ms for substring scan"
    )
    suggestion_substring_scan_pages: int = Field(
        default=10, description="Max SCAN pages per entity type during substring scan"
    )

    ***REMOVED*** Feature flags
    enable_semantic_search: bool = Field(default=False, description="Enable semantic search")
    enable_search_analytics: bool = Field(default=True, description="Enable search analytics")
    enable_fuzzy_matching: bool = Field(default=True, description="Enable fuzzy matching")
    enable_typo_tolerance: bool = Field(default=True, description="Enable typo tolerance")

    ***REMOVED*** Performance settings
    max_concurrent_searches: int = Field(default=100, description="Maximum concurrent searches")
    search_timeout_seconds: int = Field(default=30, description="Search timeout in seconds")
    suggestion_batch_size: int = Field(default=1000, description="Suggestion indexing batch size")

    ***REMOVED*** Monitoring settings

    enable_performance_metrics: bool = Field(
        default=True, description="Enable performance metrics collection"
    )
    cache_enable_metrics: bool = Field(default=True, description="Enable cache metrics collection")

    class Config:
        """Pydantic configuration for environment handling."""

        env_prefix = ""  ***REMOVED*** No prefix for environment variables
        env_file = [".env", ".env.local"]
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Search API configuration."""
        ***REMOVED*** Initialize with Pydantic Settings (will auto-load .env files)
        super().__init__(**kwargs)

        ***REMOVED*** Apply shared security and logging patterns
        self.apply_production_security_overrides()
        self._apply_search_specific_overrides()
        self.log_configuration_summary()
        self._log_search_specific_summary()

    def _apply_search_specific_overrides(self) -> None:
        """Apply search-specific production overrides."""
        if not self.is_production:
            return

        ***REMOVED*** Disable file logging in production to avoid volume permission issues
        if self.logs_dir:
            logger.warning("File logging disabled in production to avoid volume permission issues")
            object.__setattr__(self, "logs_dir", None)

    def _log_search_specific_summary(self) -> None:
        """Log search-specific configuration details."""
        ***REMOVED*** Log service URLs in compact format
        urls = {
            "backend": self.backend_api_url,
        }
        if self.ml_api_url:
            urls["ml"] = self.ml_api_url

        logger.info(f"Service URLs: {urls}")

        ***REMOVED*** Log feature flags in compact format
        logger.info(
            f"Features: semantic={self.enable_semantic_search}, "
            + f"analytics={self.enable_search_analytics}, "
            + f"fuzzy={self.enable_fuzzy_matching}, "
            + f"typo_tolerance={self.enable_typo_tolerance}"
        )

        ***REMOVED*** Log search settings
        logger.info(
            f"Search limits: max_suggestions={self.max_suggestions}, "
            + f"search_cache_ttl={self.search_cache_ttl}s, "
            + f"suggestion_cache_ttl={self.suggestion_cache_ttl}s"
        )

        ***REMOVED*** Log Redis URL
        logger.info(f"Redis URL: {self.get_redis_url_masked()}")

    @validator("backend_api_url", "ml_api_url")
    def validate_service_url(cls, v: str | None) -> str | None:
        """Validate service URL format."""
        if v is None:
            return None

        if not v.startswith(("http://", "https://")):
            raise ValueError("Service URL must start with http:// or https://")

        return v

    @validator("backend_api_timeout", "ml_api_timeout", "search_timeout_seconds")
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Timeout should not exceed 300 seconds")
        return v

    @validator("max_suggestions")
    def validate_max_suggestions(cls, v: int) -> int:
        """Validate max suggestions is reasonable."""
        if v < 1:
            raise ValueError("Max suggestions must be at least 1")
        if v > 1000:
            raise ValueError("Max suggestions should not exceed 1000")
        return v

    @validator("search_cache_ttl", "suggestion_cache_ttl")
    def validate_cache_ttl(cls, v: int) -> int:
        """Validate cache TTL is positive."""
        if v < 1:
            raise ValueError("Cache TTL must be at least 1 second")
        if v > 86400:  ***REMOVED*** 24 hours
            raise ValueError("Cache TTL should not exceed 24 hours")
        return v

    @validator("min_query_length", "max_query_length")
    def validate_query_lengths(cls, v: int) -> int:
        """Validate query length limits."""
        if v < 1:
            raise ValueError("Query length must be at least 1")
        return v

    def validate_production_settings(self) -> list[str]:
        """Validate configuration for production deployment."""
        issues = []

        ***REMOVED*** Get validation from parent classes (includes basic debug mode checks)
        issues.extend(super().validate_production_settings())
        issues.extend(self.validate_cache_production_settings())

        ***REMOVED*** Search-specific production validations
        if self.is_production:
            ***REMOVED*** Check for secure service URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url and url.startswith("http://"):
                    issues.append(f"{url_name} should use HTTPS in production")

            ***REMOVED*** Check for localhost in URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url and "localhost" in url:
                    issues.append(f"{url_name} should not use localhost in production")

        return issues

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation."""
        return f"""Search API Configuration:
  Environment: {self.environment}
  Service: {self.service_name}

  HTTP Service:
    Host: {self.host}
    Port: {self.port}
    Debug: {self.debug}
    CORS Origins: {', '.join(self.cors_origins)}
    Allowed Hosts: {', '.join(self.allowed_hosts)}

  Service URLs:
    Backend: {self.backend_api_url}
    ML: {self.ml_api_url or 'disabled'}

  Search Settings:
    Max Suggestions: {self.max_suggestions}
    Search Cache TTL: {self.search_cache_ttl}s
    Suggestion Cache TTL: {self.suggestion_cache_ttl}s
    Query Length: {self.min_query_length}-{self.max_query_length}

  Cache:
    URL: {self.get_redis_url_masked()}
    Metrics: {self.cache_enable_metrics}

  Features:
    Semantic Search: {self.enable_semantic_search}
    Search Analytics: {self.enable_search_analytics}
    Fuzzy Matching: {self.enable_fuzzy_matching}
    Typo Tolerance: {self.enable_typo_tolerance}
"""


***REMOVED*** Create singleton instance
settings = SearchAPIConfig()


def get_search_settings() -> SearchAPIConfig:
    """Get search API settings instance.

    Returns:
        SearchAPIConfig: The search API configuration instance
    """
    return settings
