"""Database configuration mixin for PostgreSQL connections.

Provides configuration for PostgreSQL database connections with connection pooling,
timeouts, and SQLAlchemy-specific settings.
"""

from typing import Any, Dict, Optional
from urllib.parse import urlparse

from pydantic import Field, validator


class DatabaseConfigMixin:
    """PostgreSQL database configuration mixin.

    This mixin provides database connection configuration that can be composed
    into service configurations. It includes connection pooling, timeouts,
    and SQLAlchemy-specific settings.

    Environment variables (with service prefix):
    - {SERVICE}_DATABASE_URL: PostgreSQL connection URL
    - {SERVICE}_DATABASE_ECHO: Enable SQL query logging
    - {SERVICE}_DATABASE_POOL_SIZE: Connection pool size
    - {SERVICE}_DATABASE_MAX_OVERFLOW: Max overflow connections
    - {SERVICE}_DATABASE_POOL_TIMEOUT: Pool checkout timeout
    - {SERVICE}_DATABASE_POOL_RECYCLE: Connection recycle time
    """

    database_url: str = Field(
        description="PostgreSQL database connection URL",
        examples=["postgresql://user:pass@localhost:5432/dbname"],
    )
    database_echo: bool = Field(
        default=False, description="Enable SQLAlchemy query logging"
    )
    database_pool_size: int = Field(
        default=5, description="Number of connections to maintain in the pool"
    )
    database_max_overflow: int = Field(
        default=10,
        description="Maximum number of connections that can overflow the pool",
    )
    database_pool_timeout: int = Field(
        default=30, description="Timeout in seconds to get connection from pool"
    )
    database_pool_recycle: int = Field(
        default=3600, description="Time in seconds to recycle connections"
    )
    database_pool_pre_ping: bool = Field(
        default=True, description="Enable connection health checks before use"
    )

    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format and scheme."""
        if not v:
            raise ValueError("Database URL cannot be empty")

        try:
            parsed = urlparse(v)
            if parsed.scheme not in ["postgresql", "postgresql+psycopg2"]:
                raise ValueError(
                    f"Unsupported database scheme: {parsed.scheme}. "
                    "Only 'postgresql' and 'postgresql+psycopg2' are supported"
                )

            if not parsed.hostname:
                raise ValueError("Database URL must include hostname")

            if not parsed.path or parsed.path == "/":
                raise ValueError("Database URL must include database name")

        except Exception as e:
            raise ValueError(f"Invalid database URL format: {e}")

        return v

    @validator("database_pool_size")
    def validate_pool_size(cls, v: int) -> int:
        """Validate pool size is positive."""
        if v < 1:
            raise ValueError("Database pool size must be at least 1")
        if v > 50:
            raise ValueError("Database pool size should not exceed 50")
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

    @validator("database_pool_recycle")
    def validate_pool_recycle(cls, v: int) -> int:
        """Validate pool recycle time is positive."""
        if v < 300:
            raise ValueError(
                "Database pool recycle time should be at least 300 seconds"
            )
        return v

    def get_database_config(self) -> Dict[str, Any]:
        """Get SQLAlchemy database configuration dictionary.

        Returns:
            Dictionary with SQLAlchemy engine configuration
        """
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": self.database_pool_recycle,
            "pool_pre_ping": self.database_pool_pre_ping,
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

    def validate_database_production_settings(self) -> list[str]:
        """Validate database configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Check for development/test databases in production
        if "localhost" in self.database_url:
            issues.append("Database should not use localhost in production")

        if "test" in self.database_url.lower():
            issues.append("Database URL appears to reference test database")

        ***REMOVED*** Check pool settings for production
        if self.database_pool_size < 3:
            issues.append("Database pool size should be at least 3 in production")

        if self.database_echo:
            issues.append("Database echo should be disabled in production")

        ***REMOVED*** Check for default credentials
        if "password" in self.database_url.lower():
            issues.append("Database URL should not contain default passwords")

        return issues
