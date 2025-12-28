"""Authentication configuration mixin.

Provides configuration for JWT authentication with straightforward settings
and validation.
"""

from datetime import timedelta
from typing import Any

from pydantic import Field, validator


class AuthConfigMixin:
    """JWT authentication configuration mixin with simplified approach.

    This mixin provides JWT authentication configuration that can be composed
    into service configurations. It includes JWT token settings, secret keys,
    and expiration times with a straightforward approach.

    Environment variables (with service prefix):
    - {SERVICE}_JWT_SECRET: Secret key for JWT token signing
    - {SERVICE}_JWT_ALGORITHM: Algorithm for JWT token signing
    - {SERVICE}_JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time
    - {SERVICE}_JWT_REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time
    """

    ***REMOVED*** JWT settings
    jwt_secret: str = Field(
        default="change_me_in_production",
        description="Secret key for JWT token signing",
    )
    jwt_algorithm: str = Field(default="HS256", description="Algorithm for JWT token signing")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration time in days"
    )
    jwt_token_prefix: str = Field(
        default="Bearer", description="Token prefix for Authorization header"
    )

    @validator("jwt_secret")
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret is not empty and has minimum length."""
        if not v:
            raise ValueError("JWT secret cannot be empty")
        if len(v) < 16:
            raise ValueError("JWT secret should be at least 16 characters long")
        return v

    @validator("jwt_algorithm")
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm is supported."""
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in allowed_algorithms:
            raise ValueError(f"JWT algorithm must be one of {allowed_algorithms}")
        return v

    @validator("jwt_access_token_expire_minutes")
    def validate_access_token_expire(cls, v: int) -> int:
        """Validate access token expiration time is positive."""
        if v < 1:
            raise ValueError("Access token expiration must be at least 1 minute")
        if v > 60 * 24:  ***REMOVED*** 24 hours
            raise ValueError("Access token expiration should not exceed 24 hours")
        return v

    @validator("jwt_refresh_token_expire_days")
    def validate_refresh_token_expire(cls, v: int) -> int:
        """Validate refresh token expiration time is positive."""
        if v < 1:
            raise ValueError("Refresh token expiration must be at least 1 day")
        if v > 90:  ***REMOVED*** 90 days
            raise ValueError("Refresh token expiration should not exceed 90 days")
        return v

    @validator("jwt_token_prefix")
    def validate_token_prefix(cls, v: str) -> str:
        """Validate token prefix is not empty."""
        if not v:
            raise ValueError("Token prefix cannot be empty")
        return v

    def get_jwt_config(self) -> dict[str, Any]:
        """Get JWT configuration dictionary.

        Returns:
            Dictionary with JWT configuration
        """
        return {
            "secret": self.jwt_secret,
            "algorithm": self.jwt_algorithm,
            "access_token_expire": timedelta(minutes=self.jwt_access_token_expire_minutes),
            "refresh_token_expire": timedelta(days=self.jwt_refresh_token_expire_days),
            "token_prefix": self.jwt_token_prefix,
        }

    def get_jwt_secret_masked(self) -> str:
        """Get JWT secret with masking for logging.

        Returns:
            JWT secret with masking
        """
        if not self.jwt_secret:
            return "***"

        ***REMOVED*** Show only first 4 characters if secret is long enough
        if len(self.jwt_secret) > 8:
            return f"{self.jwt_secret[:4]}***"
        return "***"

    def validate_auth_production_settings(self) -> list[str]:
        """Validate authentication configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Check JWT secret security
        if (
            self.jwt_secret == "change_me_in_production"
            and hasattr(self, "is_production")
            and getattr(self, "is_production")
        ):
            issues.append("JWT secret must be changed for production")

        ***REMOVED*** Check token expiration times for production
        if hasattr(self, "is_production") and getattr(self, "is_production"):
            if self.jwt_access_token_expire_minutes > 60:
                issues.append("Access token expiration should not exceed 60 minutes in production")

            if self.jwt_refresh_token_expire_days > 30:
                issues.append("Refresh token expiration should not exceed 30 days in production")

        return issues

    def log_auth_configuration(self) -> None:
        """Log auth configuration with reduced verbosity."""
        if hasattr(self, "debug") and (
            getattr(self, "debug") or getattr(self, "log_level", "INFO") == "DEBUG"
        ):
            from config.logging import get_logger

            logger = get_logger(__name__)

            ***REMOVED*** Log JWT settings in compact format
            logger.debug(
                f"JWT: algorithm={self.jwt_algorithm}, "
                + f"access_token_expire={self.jwt_access_token_expire_minutes}min, "
                + f"refresh_token_expire={self.jwt_refresh_token_expire_days}days"
            )

            ***REMOVED*** Log JWT secret (masked)
            logger.debug(f"JWT secret: {self.get_jwt_secret_masked()}")
