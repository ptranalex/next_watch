"""Base configuration classes for NextWatch services.

Provides abstract base classes and concrete implementations for different types
of services in the NextWatch platform.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings, ABC):
    """Abstract base configuration class for all NextWatch services.

    Provides common configuration fields and validation methods that all
    services should implement.
    """

    ***REMOVED*** Common fields across all services
    environment: str = Field(
        default="development", description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Base logging level")
    service_name: str = Field(description="Name of the service")
    version: str = Field(default="1.0.0", description="Service version")

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        ***REMOVED*** Handle list parsing manually through validators
        env_prefix="",
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

    @abstractmethod
    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """

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
        regardless of configuration mistakes. Services can override this to add
        service-specific security overrides.
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
        """Log service configuration summary on initialization.

        Provides a standard way for services to log their configuration
        during startup. Services can override this to add service-specific
        logging details.
        """
        from config.logging import get_logger

        logger = get_logger(__name__)

        logger.info(f"Initializing {self.service_name} configuration")
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Version: {self.version}")
        logger.info(f"Debug mode: {self.debug}")
        logger.info(f"Log level: {self.log_level}")

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as a dictionary.

        Returns:
            Configuration dictionary with all fields
        """
        return self.dict()

    def __str__(self) -> str:
        """String representation with sensitive data masked."""
        config_dict = self.get_config_dict()
        ***REMOVED*** Basic masking for display - will be enhanced by security module
        masked_dict = {}
        for key, value in config_dict.items():
            if any(
                sensitive in key.lower()
                for sensitive in ["secret", "password", "token", "key"]
            ):
                masked_dict[key] = "***"
            else:
                masked_dict[key] = value

        return f"{self.__class__.__name__}({masked_dict})"


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
    def parse_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse allowed hosts from various formats."""
        if isinstance(v, str):
            if not v.strip():
                return ["*"]
            ***REMOVED*** Handle comma-separated string
            return [host.strip() for host in v.split(",") if host.strip()]
        elif isinstance(v, list):
            return v

    @validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from various formats."""
        if isinstance(v, str):
            if not v.strip():
                return ["*"]
            ***REMOVED*** Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v

    @validator("cors_origins")
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins format."""
        if not v:
            raise ValueError("CORS origins cannot be empty")
        return v

    def validate_production_settings(self) -> List[str]:
        """Validate HTTP service configuration for production."""
        issues = []

        if self.debug:
            issues.append("Debug mode should be disabled in production")

        if "*" in self.cors_origins and self.is_production:
            issues.append("CORS origins should be specific in production (not '*')")

        if "*" in self.allowed_hosts and self.is_production:
            issues.append("Allowed hosts should be specific in production (not '*')")

        return issues


class WorkerConfig(BaseConfig):
    """Base configuration for worker services.

    Provides configuration for background workers, data processors,
    and other non-HTTP services.
    """

    workers: int = Field(default=1, description="Number of worker processes")
    max_concurrent_tasks: int = Field(
        default=10, description="Maximum concurrent tasks"
    )
    task_timeout_seconds: int = Field(
        default=300, description="Task timeout in seconds"
    )

    @validator("workers")
    def validate_workers(cls, v: int) -> int:
        """Validate worker count is positive."""
        if v < 1:
            raise ValueError("Worker count must be at least 1")
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
        """Validate worker configuration for production."""
        issues = []

        if self.debug:
            issues.append("Debug mode should be disabled in production")

        if self.workers == 1 and self.is_production:
            issues.append(
                "Consider using multiple workers in production for better performance"
            )

        return issues
