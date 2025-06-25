"""Configuration settings for the Backend API service.

This module provides centralized configuration for the backend-api application
using the shared NextWatch configuration library with type-safe validation,
enhanced security features, and production-ready defaults.

The configuration combines database, cache, authentication, and monitoring
settings with backend-api specific customizations. It leverages shared patterns
for production security overrides and configuration logging.
"""

from typing import Any, Dict, List, Optional

from config.base.config import ServiceConfig
from config.services.auth import AuthConfigMixin
from config.services.cache import CacheConfigMixin
from config.services.database import DatabaseConfigMixin
from config.services.monitoring import MonitoringConfigMixin
from pydantic import Field, validator

from config.logging import get_logger

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)


class BackendAPIConfig(
    ServiceConfig, DatabaseConfigMixin, CacheConfigMixin, AuthConfigMixin, MonitoringConfigMixin
):
    """Backend API service configuration using shared NextWatch config library.

    This configuration class combines all necessary service mixins to provide
    a comprehensive configuration for the backend API service including:
    - HTTP service configuration (host, port, CORS)
    - Database configuration (PostgreSQL with connection pooling)
    - Cache configuration (Redis with TTL management)
    - Authentication configuration (JWT with security features)
    - Monitoring configuration (logging, metrics, health checks)

    All settings can be configured via environment variables with sensible defaults.
    """

    ***REMOVED*** Service identification
    service_name: str = Field(default="backend-api", description="Service name")
    version: str = Field(default="0.1.0", description="Service version")

    ***REMOVED*** HTTP service settings (override defaults from ServiceConfig)
    host: str = Field(default="0.0.0.0", description="Service host address")
    port: int = Field(default=8000, description="Service port number")

    ***REMOVED*** Backend-specific settings
    backend_performance_metrics: bool = Field(
        default=False, description="Enable backend-specific performance metrics collection"
    )
    logs_dir: Optional[str] = Field(
        default=None, description="Directory for log files (None disables file logging)"
    )

    ***REMOVED*** Database profiling settings (development only)
    enable_db_profiling: bool = Field(
        default=False, description="Enable database query profiling (development only)"
    )
    db_profiling_slow_query_threshold_ms: int = Field(
        default=100, description="Threshold in ms for slow query profiling"
    )

    ***REMOVED*** Database monitoring settings
    database_monitoring_enabled: bool = Field(
        default=True, description="Enable database performance monitoring"
    )
    slow_query_threshold_ms: int = Field(
        default=100, description="Threshold in ms for slow query warnings"
    )

    ***REMOVED*** Authentication settings
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration time in days"
    )

    ***REMOVED*** Service-to-service authentication
    internal_api_key: str = Field(
        default="bff-to-backend-secret-key",
        description="Internal API key for service-to-service authentication",
    )

    class Config:
        """Pydantic configuration for environment handling."""

        env_file = [".env", ".env.local"]  ***REMOVED*** Load multiple env files
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize backend API configuration."""
        ***REMOVED*** Initialize with Pydantic Settings (will auto-load .env files)
        super().__init__(**kwargs)

        ***REMOVED*** Apply shared security and logging patterns
        self.apply_production_security_overrides()
        self._apply_backend_specific_overrides()
        self.log_configuration_summary()
        self._log_backend_specific_summary()

    def _apply_backend_specific_overrides(self) -> None:
        """Apply backend-specific production overrides."""
        if not self.is_production:
            return

        ***REMOVED*** Backend-specific security overrides
        if self.enable_db_profiling:
            logger.warning("Database profiling disabled in production for security and performance")
            object.__setattr__(self, "enable_db_profiling", False)

        ***REMOVED*** Disable file logging in production to avoid volume permission issues
        if self.logs_dir:
            logger.warning("File logging disabled in production to avoid volume permission issues")
            object.__setattr__(self, "logs_dir", None)

    def _log_backend_specific_summary(self) -> None:
        """Log backend-specific configuration details."""
        logger.info(f"Database URL: {self.get_database_url_masked()}")
        logger.info(f"API Port: {self.port}")
        logger.info(f"Redis URL: {self.get_redis_url_masked()}")
        logger.info(f"DB Profiling: {self.enable_db_profiling}")
        logger.info(f"DB Monitoring: {self.database_monitoring_enabled}")
        logger.info(f"Performance Metrics: {self.backend_performance_metrics}")

    @validator("enable_db_profiling")
    def validate_db_profiling(cls, v: bool, values: Dict[str, Any]) -> bool:
        """Ensure database profiling is disabled in production."""
        environment = values.get("environment", "development")
        if v and environment == "production":
            logger.warning("Database profiling disabled in production for security")
            return False
        return v

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment.

        Combines validation from all mixins plus backend-specific checks.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Get validation from parent classes (includes basic debug mode checks)
        issues.extend(super().validate_production_settings())
        issues.extend(self.validate_database_production_settings())
        issues.extend(self.validate_cache_production_settings())
        issues.extend(self.validate_auth_production_settings())
        issues.extend(self.validate_monitoring_production_settings(self.environment))

        ***REMOVED*** Backend-specific production validation
        if self.enable_db_profiling:
            issues.append("Database profiling should be disabled in production")

        if self.logs_dir:
            issues.append("File logging should be disabled in production")

        return issues

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation."""
        return f"""Backend API Configuration:
  Environment: {self.environment}
  Service: {self.service_name} v{self.version}
  
  HTTP Service:
    Host: {self.host}
    Port: {self.port}
    Debug: {self.debug}
    CORS Origins: {', '.join(self.cors_origins)}
    Allowed Hosts: {', '.join(self.allowed_hosts)}

  Database:
    URL: {self.get_database_url_masked()}

  Authentication:
    Access Token TTL: {self.access_token_expire_minutes}min
    Refresh Token TTL: {self.refresh_token_expire_days}days

  Monitoring:
    Log Level: {self.log_level}
    Performance Metrics: {self.backend_performance_metrics}
    DB Monitoring: {self.database_monitoring_enabled}
    Logs Directory: {self.logs_dir or 'disabled'}

  Cache:
    Redis URL: {self.get_redis_url_masked()}"""


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** GLOBAL SETTINGS INSTANCE
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Create global settings instance (simplified - no more wrapper!)
settings = BackendAPIConfig()
