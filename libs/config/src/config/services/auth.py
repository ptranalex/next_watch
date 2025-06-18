"""Authentication configuration mixin for JWT-based auth.

Provides configuration for JWT token management, signing, and validation
across NextWatch services.
"""

import secrets
from typing import Any, Dict, List, Optional

from pydantic import Field, validator


class AuthConfigMixin:
    """JWT authentication configuration mixin.

    This mixin provides JWT authentication configuration that can be composed
    into service configurations. It includes token signing, validation,
    and security settings.

    Environment variables (with service prefix):
    - {SERVICE}_JWT_SECRET: Secret key for JWT signing
    - {SERVICE}_JWT_ALGORITHM: JWT signing algorithm
    - {SERVICE}_ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration
    - {SERVICE}_REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration
    - {SERVICE}_JWT_AUDIENCE: JWT audience claim
    - {SERVICE}_JWT_ISSUER: JWT issuer claim
    """

    jwt_secret: str = Field(
        description="Secret key for JWT token signing and verification", min_length=32
    )
    jwt_algorithm: str = Field(
        default="HS256", description="Algorithm used for JWT signing"
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration time in days"
    )
    jwt_audience: Optional[str] = Field(
        default=None, description="JWT audience claim for token validation"
    )
    jwt_issuer: Optional[str] = Field(
        default=None, description="JWT issuer claim for token validation"
    )
    jwt_leeway_seconds: int = Field(
        default=10, description="Leeway in seconds for token expiration validation"
    )

    ***REMOVED*** Security settings
    require_https_for_tokens: bool = Field(
        default=True, description="Require HTTPS for token transmission"
    )
    token_blacklist_enabled: bool = Field(
        default=True, description="Enable token blacklisting for logout"
    )
    max_refresh_token_age_days: int = Field(
        default=30, description="Maximum age for refresh token reuse"
    )

    @validator("jwt_secret")
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret strength and format."""
        if not v:
            raise ValueError("JWT secret cannot be empty")

        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters long")

        ***REMOVED*** Check for common weak secrets
        weak_secrets = [
            "change_this_in_production_very_important",
            "super_secret_key",
            "jwt_secret_key",
            "your_secret_here",
            "default_secret",
        ]

        if v.lower() in [secret.lower() for secret in weak_secrets]:
            raise ValueError("JWT secret appears to be a default/weak value")

        ***REMOVED*** Warn about low entropy (basic check)
        unique_chars = len(set(v.lower()))
        if unique_chars < 8:
            raise ValueError("JWT secret has low entropy - use more varied characters")

        return v

    @validator("jwt_algorithm")
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm is secure."""
        allowed_algorithms = [
            "HS256",
            "HS384",
            "HS512",  ***REMOVED*** HMAC algorithms
            "RS256",
            "RS384",
            "RS512",  ***REMOVED*** RSA algorithms
            "ES256",
            "ES384",
            "ES512",  ***REMOVED*** ECDSA algorithms
        ]

        if v not in allowed_algorithms:
            raise ValueError(
                f"Unsupported JWT algorithm: {v}. "
                f"Allowed algorithms: {', '.join(allowed_algorithms)}"
            )

        ***REMOVED*** Warn about weaker algorithms in production
        if v in ["HS256"] and len(v) > 0:  ***REMOVED*** Placeholder for production check
            pass  ***REMOVED*** Could add production-specific warnings

        return v

    @validator("access_token_expire_minutes")
    def validate_access_token_expire(cls, v: int) -> int:
        """Validate access token expiration time."""
        if v < 1:
            raise ValueError("Access token expiration must be at least 1 minute")
        if v > 1440:  ***REMOVED*** 24 hours
            raise ValueError("Access token expiration should not exceed 24 hours")
        return v

    @validator("refresh_token_expire_days")
    def validate_refresh_token_expire(cls, v: int) -> int:
        """Validate refresh token expiration time."""
        if v < 1:
            raise ValueError("Refresh token expiration must be at least 1 day")
        if v > 90:  ***REMOVED*** 3 months
            raise ValueError("Refresh token expiration should not exceed 90 days")
        return v

    @validator("jwt_leeway_seconds")
    def validate_jwt_leeway(cls, v: int) -> int:
        """Validate JWT leeway time."""
        if v < 0:
            raise ValueError("JWT leeway cannot be negative")
        if v > 300:  ***REMOVED*** 5 minutes
            raise ValueError("JWT leeway should not exceed 5 minutes")
        return v

    @validator("max_refresh_token_age_days")
    def validate_max_refresh_age(cls, v: int) -> int:
        """Validate maximum refresh token age."""
        if v < 1:
            raise ValueError("Max refresh token age must be at least 1 day")
        if v > 365:  ***REMOVED*** 1 year
            raise ValueError("Max refresh token age should not exceed 1 year")
        return v

    def get_jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration dictionary.

        Returns:
            Dictionary with JWT configuration
        """
        config = {
            "secret": self.jwt_secret,
            "algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
            "leeway_seconds": self.jwt_leeway_seconds,
        }

        if self.jwt_audience:
            config["audience"] = self.jwt_audience

        if self.jwt_issuer:
            config["issuer"] = self.jwt_issuer

        return config

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration dictionary.

        Returns:
            Dictionary with security-specific configuration
        """
        return {
            "require_https": self.require_https_for_tokens,
            "blacklist_enabled": self.token_blacklist_enabled,
            "max_refresh_age_days": self.max_refresh_token_age_days,
        }

    def generate_secure_secret(self, length: int = 64) -> str:
        """Generate a cryptographically secure JWT secret.

        Args:
            length: Length of the secret to generate

        Returns:
            Secure random secret string
        """
        return secrets.token_urlsafe(length)

    def get_token_expiry_config(self) -> Dict[str, int]:
        """Get token expiry configuration in seconds.

        Returns:
            Dictionary with token expiry times in seconds
        """
        return {
            "access_token_seconds": self.access_token_expire_minutes * 60,
            "refresh_token_seconds": self.refresh_token_expire_days * 24 * 60 * 60,
            "leeway_seconds": self.jwt_leeway_seconds,
        }

    def validate_auth_production_settings(self) -> List[str]:
        """Validate authentication configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Check JWT secret strength
        if len(self.jwt_secret) < 64:
            issues.append("JWT secret should be at least 64 characters in production")

        ***REMOVED*** Check for default secrets
        if "change_this" in self.jwt_secret.lower():
            issues.append("JWT secret must be changed from default value")

        ***REMOVED*** Check token expiration times for production
        if self.access_token_expire_minutes > 60:
            issues.append(
                "Access token expiration should be 60 minutes or less in production"
            )

        if self.refresh_token_expire_days > 30:
            issues.append(
                "Refresh token expiration should be 30 days or less in production"
            )

        ***REMOVED*** Check security settings
        if not self.require_https_for_tokens:
            issues.append("HTTPS should be required for tokens in production")

        if not self.token_blacklist_enabled:
            issues.append("Token blacklisting should be enabled in production")

        ***REMOVED*** Check for audience and issuer claims
        if not self.jwt_audience:
            issues.append("JWT audience claim should be set in production")

        if not self.jwt_issuer:
            issues.append("JWT issuer claim should be set in production")

        ***REMOVED*** Check algorithm strength
        if self.jwt_algorithm in ["HS256"]:
            issues.append(
                "Consider using stronger JWT algorithm (RS256, ES256) in production"
            )

        return issues
