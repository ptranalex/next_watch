"""Configuration settings for the Authentication API service.

This module provides centralized configuration for the auth-api application
using the shared NextWatch configuration library with type-safe validation,
enhanced security features, and production-ready defaults.

The configuration combines database, cache, authentication, and monitoring
settings with auth-api specific customizations. It leverages shared patterns
for production security overrides and configuration logging.
"""

import json
from typing import Any

from config.base.config import ServiceConfig
from config.logging import get_logger
from config.services.auth import AuthConfigMixin
from config.services.database import DatabaseConfigMixin
from config.services.monitoring import MonitoringConfigMixin
from pydantic import Field, validator

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)


class AuthAPIConfig(ServiceConfig, DatabaseConfigMixin, AuthConfigMixin, MonitoringConfigMixin):
    """Authentication API service configuration using shared NextWatch config library.

    This configuration class combines all necessary service mixins to provide
    a comprehensive configuration for the authentication API service including:
    - HTTP service configuration (host, port, CORS)
    - Database configuration (PostgreSQL with connection pooling)
    - Authentication configuration (JWT with security features)
    - Monitoring configuration (logging, metrics, health checks)

    All settings can be configured via environment variables with sensible defaults.
    """

    ***REMOVED*** Service identification
    service_name: str = Field(default="auth-api", description="Service name")
    version: str = Field(default="0.1.0", description="Service version")

    ***REMOVED*** HTTP service settings (override defaults from ServiceConfig)
    host: str = Field(default="0.0.0.0", description="Service host address")
    port: int = Field(default=8003, description="Service port number")

    ***REMOVED*** Auth-specific settings
    auth_performance_metrics: bool = Field(
        default=False, description="Enable auth-specific performance metrics collection"
    )
    logs_dir: str | None = Field(
        default=None, description="Directory for log files (None disables file logging)"
    )

    ***REMOVED*** JWT Web Key settings
    jwt_jwk: dict[str, Any] | None = Field(
        default=None, description="JSON Web Key for advanced JWT validation"
    )
    jwt_jwk_rotation_interval: int = Field(
        default=86400, description="JWK rotation interval in seconds (24 hours)"
    )

    ***REMOVED*** Enhanced security settings for auth service
    require_https_production: bool = Field(
        default=True, description="Require HTTPS in production environment"
    )
    enable_session_management: bool = Field(
        default=True, description="Enable session management features"
    )
    enable_password_reset: bool = Field(
        default=True, description="Enable password reset functionality"
    )
    enable_user_registration: bool = Field(default=True, description="Enable user registration")

    class Config:
        """Pydantic configuration for environment handling."""

        env_file = [".env", ".env.local"]  ***REMOVED*** Load multiple env files
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize authentication API configuration."""
        ***REMOVED*** Initialize with Pydantic Settings (will auto-load .env files)
        super().__init__(**kwargs)

        ***REMOVED*** Apply shared security and logging patterns
        self.apply_production_security_overrides()
        self._apply_auth_specific_overrides()
        self.log_configuration_summary()
        self._log_auth_specific_summary()

    def _apply_auth_specific_overrides(self) -> None:
        """Apply auth-specific production overrides."""
        if not self.is_production:
            return

        ***REMOVED*** Auth-specific security overrides
        if not self.require_https_production:
            logger.warning("HTTPS requirement enforced in production for auth service")
            object.__setattr__(self, "require_https_production", True)

        ***REMOVED*** Disable file logging in production to avoid volume permission issues
        if self.logs_dir:
            logger.warning("File logging disabled in production to avoid volume permission issues")
            object.__setattr__(self, "logs_dir", None)

        ***REMOVED*** Ensure secure JWT settings in production
        if self.jwt_secret == "change_this_in_production_very_important":
            logger.error("Default JWT secret detected in production - this is a security risk!")
            ***REMOVED*** Don't override in production - let it fail fast

    def _log_auth_specific_summary(self) -> None:
        """Log auth-specific configuration details."""
        logger.info(f"Database URL: {self.get_database_url_masked()}")
        logger.info(f"API Port: {self.port}")
        logger.info(f"JWT Algorithm: {self.jwt_algorithm}")
        logger.info(f"JWK Enabled: {self.jwt_jwk is not None}")
        logger.info(f"Session Management: {self.enable_session_management}")
        logger.info(f"User Registration: {self.enable_user_registration}")
        logger.info(f"Password Reset: {self.enable_password_reset}")
        logger.info(f"Performance Metrics: {self.auth_performance_metrics}")

    @validator("jwt_secret")
    def validate_jwt_secret_production(cls, v: str, values: dict[str, Any]) -> str:
        """Ensure JWT secret is secure in production."""
        environment = values.get("environment", "development")
        if environment == "production" and v == "change_this_in_production_very_important":
            raise ValueError(
                "Default JWT secret is not allowed in production. "
                "Set a secure JWT_SECRET environment variable."
            )
        return v

    @validator("jwt_jwk", pre=True)
    def validate_jwt_jwk(cls, v: Any) -> dict[str, Any] | None:
        """Parse JWT JWK from string or return None for empty values."""
        if not v or v == "":
            return None
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise ValueError("JWK must be a JSON object")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JWK configuration: {e}")
                raise ValueError(f"Invalid JWK JSON format: {e}") from e
        if isinstance(v, dict):
            return v
        raise ValueError(f"JWK must be a string, dict, or None, got {type(v)}")

    @validator("cors_origins")
    def validate_cors_origins_auth(cls, v: list[str], values: dict[str, Any]) -> list[str]:
        """Validate CORS origins for auth service security."""
        environment = values.get("environment", "development")
        if environment == "production" and "*" in v:
            logger.warning(
                "Wildcard CORS origins detected in production auth service. "
                "Consider restricting to specific origins for enhanced security."
            )
        return v

    def validate_production_settings(self) -> list[str]:
        """Validate configuration for production deployment.

        Combines validation from all mixins plus auth-specific checks.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Get validation from parent classes
        issues.extend(super().validate_production_settings())
        issues.extend(self.validate_database_production_settings())
        issues.extend(self.validate_auth_production_settings())
        issues.extend(self.validate_monitoring_production_settings(self.environment))

        ***REMOVED*** Auth-specific production validation
        if self.is_production:
            if not self.require_https_production:
                issues.append("HTTPS should be required in production for auth service")

            if self.logs_dir:
                issues.append("File logging should be disabled in production")

            if self.jwt_secret == "change_this_in_production_very_important":
                issues.append("Default JWT secret must be changed in production")

        return issues

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation."""
        return f"""Authentication API Configuration:
  Environment: {self.environment}
  Service: {self.service_name} v{self.version}


  HTTP Service:
    Host: {self.host}
    Port: {self.port}
    Debug: {self.debug}
    CORS Origins: {", ".join(self.cors_origins)}
    Allowed Hosts: {", ".join(self.allowed_hosts)}

  Database:
    URL: {self.get_database_url_masked()}

  Authentication:
    JWT Algorithm: {self.jwt_algorithm}
    Access Token TTL: {self.jwt_access_token_expire_minutes}min
    Refresh Token TTL: {self.jwt_refresh_token_expire_days}days
    JWK Enabled: {self.jwt_jwk is not None}
    Session Management: {self.enable_session_management}

  Security:
    Require HTTPS (Prod): {self.require_https_production}
    User Registration: {self.enable_user_registration}
    Password Reset: {self.enable_password_reset}

  Monitoring:
    Log Level: {self.log_level}
    Performance Metrics: {self.auth_performance_metrics}
    Logs Directory: {self.logs_dir or "disabled"}"""


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** GLOBAL SETTINGS INSTANCE
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Create global settings instance (simplified - no more wrapper!)
settings = AuthAPIConfig()
