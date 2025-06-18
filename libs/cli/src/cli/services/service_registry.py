"""Service registry for service discovery and configuration management.

Provides centralized service registration and discovery patterns based on
the enterprise requirements discovered in BFF API CLI analysis.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Protocol
from urllib.parse import urlparse

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a registered service.

    Based on patterns from BFF API CLI where services have different
    timeout, retry, and endpoint configurations.
    """

    name: str
    url: str
    timeout: int = 10
    retry_attempts: int = 3
    retry_backoff: str = "exponential"
    health_endpoint: str = "/health"
    service_type: str = "http"
    headers: Dict[str, str] = field(default_factory=dict)
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate service configuration."""
        ***REMOVED*** Validate URL
        try:
            parsed = urlparse(self.url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid service URL: {self.url}")
        except Exception as e:
            raise ValueError(f"Invalid service URL '{self.url}': {e}") from e

        ***REMOVED*** Validate timeout
        if self.timeout <= 0:
            raise ValueError("Service timeout must be positive")

        ***REMOVED*** Validate retry attempts
        if self.retry_attempts < 0:
            raise ValueError("Retry attempts cannot be negative")

        ***REMOVED*** Validate retry backoff strategy
        valid_backoff = ["linear", "exponential", "fixed"]
        if self.retry_backoff not in valid_backoff:
            raise ValueError(
                f"Invalid retry backoff: {self.retry_backoff}. Must be one of {valid_backoff}"
            )

    @property
    def base_url(self) -> str:
        """Get the base URL without trailing slashes."""
        return self.url.rstrip("/")

    @property
    def health_url(self) -> str:
        """Get the full health check URL."""
        return f"{self.base_url}{self.health_endpoint}"


class ConfigProvider(Protocol):
    """Protocol for configuration providers.

    Allows different ways to provide service configuration
    (from config objects, environment, etc.)
    """

    def get_services(self) -> List[ServiceConfig]:
        """Get list of service configurations."""
        ...


class ServiceRegistry:
    """Registry for service discovery and configuration management.

    Provides centralized service registration with enterprise patterns
    for timeout, retry, and health check configuration.
    """

    def __init__(self) -> None:
        """Initialize empty service registry."""
        self._services: Dict[str, ServiceConfig] = {}
        self.logger = logger.bind(component="service_registry")

    def register_service(self, config: ServiceConfig) -> None:
        """Register a service in the registry.

        Args:
            config: Service configuration to register

        Raises:
            ValueError: If service name already registered or config invalid
        """
        if config.name in self._services:
            raise ValueError(f"Service '{config.name}' is already registered")

        self._services[config.name] = config
        self.logger.info(
            "Service registered",
            service_name=config.name,
            service_url=config.url,
            service_type=config.service_type,
            timeout=config.timeout,
            retry_attempts=config.retry_attempts,
        )

    def register_services(self, configs: List[ServiceConfig]) -> None:
        """Register multiple services.

        Args:
            configs: List of service configurations to register
        """
        for config in configs:
            self.register_service(config)

    def get_service(self, name: str) -> ServiceConfig:
        """Get service configuration by name.

        Args:
            name: Service name

        Returns:
            Service configuration

        Raises:
            KeyError: If service not found
        """
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found in registry")

        return self._services[name]

    def list_services(self) -> List[str]:
        """Get list of registered service names.

        Returns:
            List of service names
        """
        return list(self._services.keys())

    def get_services_by_type(self, service_type: str) -> List[ServiceConfig]:
        """Get all services of a specific type.

        Args:
            service_type: Type of services to retrieve (e.g., "http", "redis")

        Returns:
            List of matching service configurations
        """
        return [
            config
            for config in self._services.values()
            if config.service_type == service_type
        ]

    def is_registered(self, name: str) -> bool:
        """Check if a service is registered.

        Args:
            name: Service name to check

        Returns:
            True if service is registered, False otherwise
        """
        return name in self._services

    def unregister_service(self, name: str) -> None:
        """Unregister a service.

        Args:
            name: Service name to unregister

        Raises:
            KeyError: If service not found
        """
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found in registry")

        del self._services[name]
        self.logger.info("Service unregistered", service_name=name)

    def clear(self) -> None:
        """Clear all registered services."""
        service_count = len(self._services)
        self._services.clear()
        self.logger.info("Service registry cleared", removed_count=service_count)

    @classmethod
    def from_config_provider(cls, provider: ConfigProvider) -> "ServiceRegistry":
        """Create registry from a configuration provider.

        Args:
            provider: Configuration provider implementing ConfigProvider protocol

        Returns:
            Populated service registry
        """
        registry = cls()
        configs = provider.get_services()
        registry.register_services(configs)
        return registry

    @classmethod
    def from_dict(cls, services_config: Dict[str, Dict[str, Any]]) -> "ServiceRegistry":
        """Create registry from dictionary configuration.

        Args:
            services_config: Dictionary mapping service names to their configurations

        Returns:
            Populated service registry

        Example:
            services = {
                "backend_api": {
                    "url": "http://localhost:8000",
                    "timeout": 10,
                    "retry_attempts": 3
                },
                "auth_api": {
                    "url": "http://localhost:8003",
                    "timeout": 5,
                    "retry_attempts": 2
                }
            }
            registry = ServiceRegistry.from_dict(services)
        """
        registry = cls()

        for service_name, config_dict in services_config.items():
            ***REMOVED*** Ensure the name is set in the config
            config_dict["name"] = service_name
            config = ServiceConfig(**config_dict)
            registry.register_service(config)

        return registry

    def __len__(self) -> int:
        """Return number of registered services."""
        return len(self._services)

    def __contains__(self, name: str) -> bool:
        """Check if service is registered using 'in' operator."""
        return name in self._services

    def __iter__(self) -> Iterator[str]:
        """Iterate over service names."""
        return iter(self._services)

    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"ServiceRegistry(services={list(self._services.keys())})"
