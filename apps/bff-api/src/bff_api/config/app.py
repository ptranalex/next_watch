"""BFF API service configuration.

Provides configuration for the BFF API service using the simplified config library.
"""

from typing import List, Optional, Dict, Any

from pydantic import Field, validator
from config.base.config import ServiceConfig
from config.services.cache import CacheConfigMixin
from config.services.auth import AuthConfigMixin
from config.services.monitoring import MonitoringConfigMixin
from config.profiles.service_profiles import apply_profiles, GatewayProfile

from config.logging import get_logger

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)


class BFFAPIConfig(ServiceConfig, CacheConfigMixin, AuthConfigMixin, MonitoringConfigMixin):
    """BFF API service configuration.

    Provides configuration for the BFF API service with cache, auth, and monitoring support.
    """

    ***REMOVED*** Service identification
    service_name: str = Field(default="bff-api", description="Service name")
    port: int = Field(default=8001, description="Service port")

    ***REMOVED*** Logging configuration
    logs_dir: Optional[str] = Field(
        default=None, description="Directory for log files (None disables file logging)"
    )

    ***REMOVED*** Backend service URLs
    backend_api_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    auth_api_url: str = Field(default="http://localhost:8003", description="Auth API URL")
    reco_api_url: str = Field(
        default="http://localhost:8002",
        description="Recommendation API URL",
    )
    search_api_url: str = Field(default="http://localhost:8005", description="Search API URL")
    ml_api_url: Optional[str] = Field(default=None, description="ML API URL (optional)")

    ***REMOVED*** Service timeouts
    backend_api_timeout: int = Field(default=30, description="Backend API timeout in seconds")
    auth_api_timeout: int = Field(default=10, description="Auth API timeout in seconds")
    recommendation_api_timeout: int = Field(
        default=30, description="Recommendation API timeout in seconds"
    )
    search_api_timeout: int = Field(default=15, description="Search API timeout in seconds")
    ml_api_timeout: int = Field(default=60, description="ML API timeout in seconds")

    ***REMOVED*** Service-to-service authentication
    internal_api_key: str = Field(
        default="bff-to-backend-secret-key",
        description="API key for service-to-service authentication",
    )

    ***REMOVED*** Admin/operations authentication
    admin_api_key: Optional[str] = Field(
        default=None,
        description="API key for admin endpoints (set in production for security)",
    )

    ***REMOVED*** Feature flags
    enable_recommendations: bool = Field(default=True, description="Enable recommendation features")
    enable_ml_features: bool = Field(default=False, description="Enable machine learning features")
    enable_auth_service: bool = Field(
        default=True, description="Enable authentication service integration"
    )

    ***REMOVED*** Monitoring settings
    enable_performance_metrics: bool = Field(
        default=True, description="Enable performance metrics collection"
    )

    cache_enable_metrics: bool = Field(default=True, description="Enable cache metrics collection")

    class Config:
        """Pydantic configuration for environment handling."""

        env_prefix = ""  ***REMOVED*** Remove BFF_ prefix requirement
        env_file = [".env", ".env.local"]
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize BFF API configuration."""
        ***REMOVED*** Initialize with Pydantic Settings (will auto-load .env files)
        super().__init__(**kwargs)

        ***REMOVED*** Apply shared security and logging patterns
        self.apply_production_security_overrides()
        self._apply_bff_specific_overrides()
        self.log_configuration_summary()
        self._log_bff_specific_summary()

    def _apply_bff_specific_overrides(self) -> None:
        """Apply BFF-specific production overrides."""
        if not self.is_production:
            return

        ***REMOVED*** Disable file logging in production to avoid volume permission issues
        if self.logs_dir:
            logger.warning("File logging disabled in production to avoid volume permission issues")
            object.__setattr__(self, "logs_dir", None)

    def _log_bff_specific_summary(self) -> None:
        """Log BFF-specific configuration details."""
        ***REMOVED*** Log service URLs in compact format
        urls = {
            "backend": self.backend_api_url,
            "auth": self.auth_api_url,
            "reco": self.reco_api_url,
            "search": self.search_api_url,
        }
        if self.ml_api_url:
            urls["ml"] = self.ml_api_url

        logger.info(f"Service URLs: {urls}")

        ***REMOVED*** Log feature flags in compact format if enabled
        if any([self.enable_recommendations, self.enable_ml_features, self.enable_auth_service]):
            logger.info(
                f"Features: recommendations={self.enable_recommendations}, "
                + f"ml={self.enable_ml_features}, auth={self.enable_auth_service}"
            )

        ***REMOVED*** Log Redis URL
        logger.info(f"Redis URL: {self.get_redis_url_masked()}")

    @validator("backend_api_url", "auth_api_url", "reco_api_url", "search_api_url", "ml_api_url")
    def validate_service_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate service URL format."""
        if v is None:
            return None

        if not v.startswith(("http://", "https://")):
            raise ValueError("Service URL must start with http:// or https://")

        return v

    @validator(
        "backend_api_timeout",
        "auth_api_timeout",
        "recommendation_api_timeout",
        "search_api_timeout",
        "ml_api_timeout",
    )
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Timeout should not exceed 300 seconds")
        return v

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment."""
        issues = []

        ***REMOVED*** Get validation from parent classes (includes basic debug mode checks)
        issues.extend(super().validate_production_settings())
        issues.extend(self.validate_cache_production_settings())
        issues.extend(self.validate_auth_production_settings())

        ***REMOVED*** BFF-specific production validations
        if self.is_production:
            ***REMOVED*** Check for secure service URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("auth_api_url", self.auth_api_url),
                ("reco_api_url", self.reco_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url and url.startswith("http://"):
                    issues.append(f"{url_name} should use HTTPS in production")

            ***REMOVED*** Check for localhost in URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("auth_api_url", self.auth_api_url),
                ("reco_api_url", self.reco_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url and "localhost" in url:
                    issues.append(f"{url_name} should not use localhost in production")

        return issues

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation."""
        return f"""BFF API Configuration:
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
    Auth: {self.auth_api_url}
    Recommendation: {self.reco_api_url}
    ML: {self.ml_api_url or 'disabled'}

  Cache:
    URL: {self.get_redis_url_masked()}

  Features:
    Recommendations: {self.enable_recommendations}
    ML Features: {self.enable_ml_features}
    Auth Service: {self.enable_auth_service}
    Performance Metrics: {self.enable_performance_metrics}

  Logging:
    Log Level: {self.log_level}
    Logs Directory: {self.logs_dir or 'disabled'}"""


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** GLOBAL SETTINGS INSTANCE
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Create global settings instance (simplified - no more wrapper!)
settings = BFFAPIConfig()

***REMOVED*** Apply Gateway profile by default
apply_profiles(settings, GatewayProfile)

***REMOVED*** Override log level for development
if settings.is_development:
    object.__setattr__(settings, "log_level", "DEBUG")


***REMOVED*** Backward compatibility function for cache settings
def get_cache_settings() -> Any:
    """Get cache settings from the global configuration.

    Returns:
        Cache settings dictionary
    """
    from cache.config import CacheSettings

    try:
        cache_settings = CacheSettings(
            redis_url=settings.redis_url,
            cache_key_prefix=settings.cache_key_prefix,
            cache_ttl_default=settings.cache_ttl_default,
        )
        return cache_settings
    except Exception:
        ***REMOVED*** Fallback to basic dict if CacheSettings import fails
        return {
            "redis_url": settings.redis_url,
            "cache_key_prefix": settings.cache_key_prefix,
            "cache_ttl_default": settings.cache_ttl_default,
        }
