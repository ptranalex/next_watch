"""Database configuration mixin.

Provides configuration for database connections with straightforward settings
and validation.
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from pydantic import Field, validator


class DatabaseConfigMixin:
    """Database configuration mixin with simplified approach.

    This mixin provides database connection configuration that can be composed
    into service configurations. It includes connection settings and pool
    configuration with a straightforward approach.

    Environment variables (with service prefix):
    - {SERVICE}_DATABASE_URL: Database connection URL
    - {SERVICE}_DATABASE_POOL_SIZE: Connection pool size
    - {SERVICE}_DATABASE_MAX_OVERFLOW: Maximum overflow connections
    - {SERVICE}_DATABASE_POOL_TIMEOUT: Connection pool timeout in seconds
    - {SERVICE}_DATABASE_ECHO: Enable SQL query logging
    """

    ***REMOVED*** Database connection settings
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL",
    )
    database_pool_size: int = Field(default=5, description="Connection pool size")
    database_max_overflow: int = Field(default=10, description="Maximum overflow connections")
    database_pool_timeout: int = Field(default=30, description="Connection pool timeout in seconds")
    database_echo: bool = Field(default=False, description="Enable SQL query logging")
    database_echo_pool: bool = Field(default=False, description="Enable connection pool logging")

    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format and scheme."""
        if not v:
            raise ValueError("Database URL cannot be empty")

        try:
            parsed = urlparse(v)
            if not parsed.scheme:
                raise ValueError("Database URL must include scheme")

            allowed_schemes = ["sqlite", "postgresql", "mysql", "oracle", "mssql"]
            if parsed.scheme not in allowed_schemes and not any(
                parsed.scheme.startswith(f"{scheme}+") for scheme in allowed_schemes
            ):
                raise ValueError(
                    f"Unsupported database scheme: {parsed.scheme}. "
                    f"Allowed schemes: {', '.join(allowed_schemes)}"
                )

            if parsed.scheme != "sqlite" and not parsed.hostname:
                raise ValueError("Database URL must include hostname")

        except Exception as e:
            raise ValueError(f"Invalid database URL format: {e}")

        return v

    @validator("database_pool_size")
    def validate_pool_size(cls, v: int) -> int:
        """Validate pool size is positive."""
        if v < 1:
            raise ValueError("Database pool size must be at least 1")
        if v > 100:
            raise ValueError("Database pool size should not exceed 100")
        return v

    @validator("database_max_overflow")
    def validate_max_overflow(cls, v: int) -> int:
        """Validate max overflow is non-negative."""
        if v < 0:
            raise ValueError("Database max overflow cannot be negative")
        if v > 100:
            raise ValueError("Database max overflow should not exceed 100")
        return v

    @validator("database_pool_timeout")
    def validate_pool_timeout(cls, v: int) -> int:
        """Validate pool timeout is positive."""
        if v < 1:
            raise ValueError("Database pool timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Database pool timeout should not exceed 300 seconds")
        return v

    def get_database_config(self) -> Dict[str, Any]:
        """Get database connection configuration dictionary.

        Returns:
            Dictionary with database connection configuration
        """
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "echo": self.database_echo,
            "echo_pool": self.database_echo_pool,
        }

    def get_database_url_masked(self) -> str:
        """Get database URL with credentials masked for logging.

        Returns:
            Database URL with password masked
        """
        try:
            parsed = urlparse(self.database_url)
            if parsed.password:
                masked_url = self.database_url.replace(f":{parsed.password}@", ":***@")
                return masked_url
            return self.database_url
        except Exception:
            return "***"

    def validate_database_production_settings(self) -> List[str]:
        """Validate database configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Check database URL security
        if (
            self.database_url.startswith("sqlite")
            and hasattr(self, "is_production")
            and getattr(self, "is_production")
        ):
            issues.append("SQLite should not be used in production")

        if (
            "localhost" in self.database_url
            and hasattr(self, "is_production")
            and getattr(self, "is_production")
        ):
            issues.append("Database URL should not use localhost in production")

        ***REMOVED*** Check connection pool settings
        if hasattr(self, "is_production") and getattr(self, "is_production"):
            if self.database_pool_size < 5:
                issues.append("Database pool size should be at least 5 in production")

            if self.database_echo:
                issues.append("SQL query logging should be disabled in production")

        return issues

    def log_database_configuration(self) -> None:
        """Log database configuration with reduced verbosity."""
        if hasattr(self, "debug") and (
            getattr(self, "debug") or getattr(self, "log_level", "INFO") == "DEBUG"
        ):
            from config.logging import get_logger

            logger = get_logger(__name__)

            ***REMOVED*** Log database URL (masked)
            logger.debug(f"Database: {self.get_database_url_masked()}")

            ***REMOVED*** Log pool settings in compact format
            logger.debug(
                f"DB pool: size={self.database_pool_size}, "
                + f"max_overflow={self.database_max_overflow}, "
                + f"timeout={self.database_pool_timeout}s"
            )
