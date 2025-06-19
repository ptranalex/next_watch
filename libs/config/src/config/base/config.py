"""Base configuration classes for NextWatch services.

Provides base classes for different types of services in the NextWatch platform
with a simplified, straightforward approach to configuration.
"""

from typing import Any, Dict, List, Optional, ClassVar
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration class for all NextWatch services.

    Provides common configuration fields and validation methods that all
    services should implement with a simplified approach.
    """

    ***REMOVED*** Common fields across all services
    environment: str = Field(default="development", description="Deployment environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Base logging level")
    service_name: str = Field(description="Name of the service")
    version: str = Field(default="1.0.0", description="Service version")

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed_environments = ["development", "staging", "production", "test"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid logging level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v_upper

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        ***REMOVED*** Basic production checks
        if self.environment == "production":
            if self.debug:
                issues.append("Debug mode should be disabled in production")

        return issues

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == "staging"

    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment == "test"

    def apply_production_security_overrides(self) -> None:
        """Apply production-specific security overrides.

        This method ensures critical security settings are enforced in production
        regardless of configuration mistakes.
        """
        if not self.is_production:
            return

        from config.logging import get_logger

        logger = get_logger(__name__)

        ***REMOVED*** Force disable debug mode in production
        if self.debug:
            logger.warning(f"Debug mode disabled in production for {self.service_name}")
            object.__setattr__(self, "debug", False)

    def log_configuration_summary(self) -> None:
        """Log service configuration summary with reduced verbosity."""
        from config.logging import get_logger

        logger = get_logger(__name__)

        ***REMOVED*** Basic service info - always log this
        logger.info(f"Initializing {self.service_name} ({self.environment})")

        ***REMOVED*** Group related settings
        if self.debug:
            logger.info(f"Debug mode enabled, log level: {self.log_level}")
        else:
            logger.info(f"Log level: {self.log_level}")

        ***REMOVED*** Only log detailed configuration in debug mode
        if self.debug or self.log_level == "DEBUG":
            logger.debug(f"Service version: {self.version}")
            logger.debug(f"Config hash: {self.config_hash}")

    @property
    def config_hash(self) -> str:
        """Computed hash of configuration for cache invalidation."""
        import hashlib

        config_str = f"{self.environment}_{self.service_name}_{self.version}_{self.debug}"
        return hashlib.md5(config_str.encode()).hexdigest()[:8]

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as a dictionary.

        Returns:
            Dictionary with configuration values
        """
        return self.model_dump()

    def __str__(self) -> str:
        """Return a string representation of the configuration."""
        return f"{self.service_name} Configuration (Environment: {self.environment})"


class ServiceConfig(BaseConfig):
    """Base configuration for HTTP services.

    Provides common HTTP service configuration fields like host, port,
    CORS settings, etc.
    """

    host: str = Field(default="0.0.0.0", description="Service host address")
    port: int = Field(description="Service port number")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed host headers")

    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v: Any) -> List[str]:
        """Parse allowed hosts from string or list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v or []

    @validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v or []

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration dictionary.

        Returns:
            Dictionary with server configuration
        """
        return {
            "host": self.host,
            "port": self.port,
            "cors_origins": self.cors_origins,
            "allowed_hosts": self.allowed_hosts,
        }

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = super().validate_production_settings()

        if self.is_production:
            ***REMOVED*** Check CORS settings
            if "*" in self.cors_origins:
                issues.append("Wildcard CORS origin should not be used in production")

            ***REMOVED*** Check allowed hosts
            if "*" in self.allowed_hosts:
                issues.append("Wildcard allowed hosts should not be used in production")

        return issues

    def log_configuration_summary(self) -> None:
        """Log service configuration summary with reduced verbosity."""
        ***REMOVED*** Call parent method first
        super().log_configuration_summary()

        from config.logging import get_logger

        logger = get_logger(__name__)

        ***REMOVED*** Log HTTP service info in compact format
        logger.info(f"HTTP service: {self.host}:{self.port}")

        ***REMOVED*** Only log detailed configuration in debug mode
        if self.debug or self.log_level == "DEBUG":
            ***REMOVED*** Log CORS and allowed hosts settings
            if len(self.cors_origins) == 1 and self.cors_origins[0] == "*":
                logger.debug("CORS: Allow all origins")
            else:
                logger.debug(f"CORS origins: {self.cors_origins}")

            if len(self.allowed_hosts) == 1 and self.allowed_hosts[0] == "*":
                logger.debug("Allowed hosts: All")
            else:
                logger.debug(f"Allowed hosts: {self.allowed_hosts}")


class WorkerConfig(BaseConfig):
    """Base configuration for worker services.

    Provides configuration for background workers, data processors,
    and other non-HTTP services.
    """

    workers: int = Field(default=1, description="Number of worker processes")
    max_concurrent_tasks: int = Field(default=10, description="Maximum concurrent tasks")
    task_timeout_seconds: int = Field(default=300, description="Task timeout in seconds")

    @validator("workers")
    def validate_workers(cls, v: int) -> int:
        """Validate workers is positive."""
        if v < 1:
            raise ValueError("Number of workers must be at least 1")
        return v

    @validator("max_concurrent_tasks")
    def validate_max_concurrent_tasks(cls, v: int) -> int:
        """Validate max concurrent tasks is positive."""
        if v < 1:
            raise ValueError("Max concurrent tasks must be at least 1")
        return v

    @validator("task_timeout_seconds")
    def validate_task_timeout(cls, v: int) -> int:
        """Validate task timeout is positive."""
        if v < 1:
            raise ValueError("Task timeout must be at least 1 second")
        return v

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = super().validate_production_settings()

        if self.is_production:
            ***REMOVED*** Ensure workers are properly configured for production
            if self.workers < 2:
                issues.append("At least 2 workers recommended for production")

        return issues

    def log_configuration_summary(self) -> None:
        """Log service configuration summary with reduced verbosity."""
        ***REMOVED*** Call parent method first
        super().log_configuration_summary()

        from config.logging import get_logger

        logger = get_logger(__name__)

        ***REMOVED*** Log worker settings in compact format
        logger.info(f"Worker config: {self.workers} workers, {self.max_concurrent_tasks} max tasks")

        ***REMOVED*** Only log detailed configuration in debug mode
        if self.debug or self.log_level == "DEBUG":
            logger.debug(f"Task timeout: {self.task_timeout_seconds} seconds")
