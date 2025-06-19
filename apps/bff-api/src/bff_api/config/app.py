"""BFF API service configuration.

Provides configuration for the BFF API service using the simplified config library.
"""

from typing import List, Optional, Dict, Any

from pydantic import Field, validator
from pydantic_settings import SettingsConfigDict
from config.base.config import ServiceConfig
from config.services.cache import CacheConfigMixin
from config.services.auth import AuthConfigMixin
from config.profiles.service_profiles import apply_profiles, GatewayProfile


class BFFAPIConfig(ServiceConfig, CacheConfigMixin, AuthConfigMixin):
    """BFF API service configuration.

    Provides configuration for the BFF API service with cache and auth support.
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
    auth_api_url: str = Field(default="http://localhost:8002", description="Auth API URL")
    recommendation_api_url: str = Field(
        default="http://localhost:8003", description="Recommendation API URL"
    )
    ***REMOVED*** Backwards compatibility field
    reco_api_url: str = Field(
        default="http://localhost:8003", description="Alias for recommendation_api_url"
    )
    ml_api_url: Optional[str] = Field(default=None, description="ML API URL (optional)")

    ***REMOVED*** Service timeouts
    backend_api_timeout: int = Field(default=30, description="Backend API timeout in seconds")
    auth_api_timeout: int = Field(default=10, description="Auth API timeout in seconds")
    recommendation_api_timeout: int = Field(
        default=30, description="Recommendation API timeout in seconds"
    )
    ml_api_timeout: int = Field(default=60, description="ML API timeout in seconds")

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
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    cache_enable_metrics: bool = Field(default=True, description="Enable cache metrics collection")

    model_config = SettingsConfigDict(
        env_prefix="BFF_",
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @validator("backend_api_url", "auth_api_url", "recommendation_api_url", "ml_api_url")
    def validate_service_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate service URL format."""
        if v is None:
            return None

        if not v.startswith(("http://", "https://")):
            raise ValueError("Service URL must start with http:// or https://")

        return v

    @validator(
        "backend_api_timeout", "auth_api_timeout", "recommendation_api_timeout", "ml_api_timeout"
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
        issues = super().validate_production_settings()

        ***REMOVED*** Add cache and auth validation
        issues.extend(self.validate_cache_production_settings())
        issues.extend(self.validate_auth_production_settings())

        ***REMOVED*** BFF-specific production validations
        if self.is_production:
            ***REMOVED*** Check for secure service URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("auth_api_url", self.auth_api_url),
                ("recommendation_api_url", self.recommendation_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url and url.startswith("http://"):
                    issues.append(f"{url_name} should use HTTPS in production")

            ***REMOVED*** Check for localhost in URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("auth_api_url", self.auth_api_url),
                ("recommendation_api_url", self.recommendation_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url and "localhost" in url:
                    issues.append(f"{url_name} should not use localhost in production")

        return issues

    def log_configuration_summary(self) -> None:
        """Log service configuration summary with reduced verbosity."""
        ***REMOVED*** Call parent method first (includes basic service info)
        super().log_configuration_summary()

        from config.logging import get_logger

        logger = get_logger(__name__)

        ***REMOVED*** Log service URLs in compact format
        urls = {
            "backend": self.backend_api_url,
            "auth": self.auth_api_url,
            "reco": self.recommendation_api_url,
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

        ***REMOVED*** Call mixin logging methods for detailed logs in debug mode
        if hasattr(self, "log_cache_configuration"):
            self.log_cache_configuration()

        if hasattr(self, "log_auth_configuration"):
            self.log_auth_configuration()


***REMOVED*** Create and configure the application config instance
def get_settings() -> BFFAPIConfig:
    """Get the application configuration instance.

    Returns:
        Configured BFFAPIConfig instance
    """
    config = BFFAPIConfig()

    ***REMOVED*** Apply Gateway profile by default
    apply_profiles(config, GatewayProfile)

    ***REMOVED*** Override log level for development
    if config.is_development:
        config.log_level = "DEBUG"

    ***REMOVED*** Apply production security overrides
    config.apply_production_security_overrides()

    ***REMOVED*** Log configuration summary
    config.log_configuration_summary()

    return config


***REMOVED*** Global configuration instance
settings = get_settings()


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
            key_prefix=settings.cache_key_prefix,
            ttl_default=settings.cache_ttl_default,
        )
        return cache_settings
    except Exception:
        ***REMOVED*** Fallback to basic dict if CacheSettings import fails
        return {
            "redis_url": settings.redis_url,
            "key_prefix": settings.cache_key_prefix,
            "ttl_default": settings.cache_ttl_default,
        }
