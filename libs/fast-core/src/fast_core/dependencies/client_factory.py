"""Service Client Factory for Fast Core.

This module provides a flexible factory system for creating and managing
service clients with support for custom client types, singleton patterns,
and automatic configuration.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

import httpx
from config.logging import get_logger

from .singleton import get_singleton, register_singleton

# Import tracing functionality
try:
    from fast_core.middleware.context import get_request_context

    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

logger = get_logger(__name__)

T = TypeVar("T")


class ServiceClientConfig:
    """Configuration for service clients."""

    def __init__(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        headers: dict[str, str] | None = None,
        singleton: bool = False,
        client_class: type | None = None,
        client_kwargs: dict[str, Any] | None = None,
        enable_tracing: bool = True,
        trace_service_name: str | None = None,
    ):
        """Initialize service client configuration.

        Args:
            name: Unique name for the service client
            base_url: Base URL for the service
            timeout: Request timeout in seconds
            headers: Default headers for requests
            singleton: Whether to use singleton pattern
            client_class: Custom client class (defaults to httpx.AsyncClient)
            client_kwargs: Additional kwargs for client initialization
            enable_tracing: Whether to enable automatic trace propagation
            trace_service_name: Service name for tracing (defaults to name)
        """
        self.name = name
        self.base_url = base_url
        self.timeout = timeout
        self.headers = headers or {}
        self.singleton = singleton
        self.client_class = client_class or httpx.AsyncClient
        self.client_kwargs = client_kwargs or {}
        self.enable_tracing = enable_tracing
        self.trace_service_name = trace_service_name or name


class BaseServiceClient(ABC):
    """Base class for service clients."""

    def __init__(self, config: ServiceClientConfig):
        """Initialize base service client.

        Args:
            config: Service client configuration
        """
        self.config = config
        self.name = config.name
        self.base_url = config.base_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.config.timeout,
                headers=self.config.headers,
                **self.config.client_kwargs,
            )
        return self._client

    def _get_request_headers(
        self, additional_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """Get headers for current request with automatic trace injection.

        Args:
            additional_headers: Additional headers to include

        Returns:
            Headers dictionary with trace context injected
        """
        # Start with base headers from config
        headers = dict(self.config.headers)

        # Add any additional headers provided
        if additional_headers:
            headers.update(additional_headers)

        # Add automatic trace headers if tracing is enabled
        if self.config.enable_tracing and TRACING_AVAILABLE:
            try:
                context = get_request_context()
                if context:
                    # Inject trace propagation headers
                    trace_headers = context.get_propagation_headers()
                    headers.update(trace_headers)

                    logger.debug(
                        f"Injected trace headers for {self.name}",
                        trace_headers=list(trace_headers.keys()),
                        request_id=context.request_id,
                        service=self.config.trace_service_name,
                    )
            except Exception as e:
                logger.debug(
                    f"No trace context available for {self.name}: {e}",
                    service=self.config.trace_service_name,
                )

        return headers

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the service."""


class GenericServiceClient(BaseServiceClient):
    """Generic service client for simple HTTP operations."""

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return {
                "service": self.name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "url": str(client.base_url),
            }
        except Exception as e:
            logger.warning(f"Health check failed for {self.name}: {e}")
            return {
                "service": self.name,
                "status": "error",
                "error": str(e),
                "url": self.base_url,
            }

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make GET request with automatic trace header injection."""
        client = await self._get_client()
        # Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.get(path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make POST request with automatic trace header injection."""
        client = await self._get_client()
        # Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.post(path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make PUT request with automatic trace header injection."""
        client = await self._get_client()
        # Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make DELETE request with automatic trace header injection."""
        client = await self._get_client()
        # Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.delete(path, **kwargs)


class ServiceClientFactory:
    """Factory for creating and managing service clients."""

    def __init__(self) -> None:
        """Initialize service client factory."""
        self._configs: dict[str, ServiceClientConfig] = {}
        self._client_types: dict[str, type[BaseServiceClient]] = {}
        self._instances: dict[str, Any] = {}

    def register_service(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        headers: dict[str, str] | None = None,
        singleton: bool = False,
        client_class: type | None = None,
        client_kwargs: dict[str, Any] | None = None,
        enable_tracing: bool = True,
        trace_service_name: str | None = None,
    ) -> None:
        """Register a service configuration.

        Args:
            name: Unique service name
            base_url: Service base URL
            timeout: Request timeout in seconds
            headers: Default headers
            singleton: Whether to use singleton pattern
            client_class: Custom client class
            client_kwargs: Additional client kwargs
            enable_tracing: Whether to enable automatic trace propagation
            trace_service_name: Service name for tracing (defaults to name)
        """
        config = ServiceClientConfig(
            name=name,
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            singleton=singleton,
            client_class=client_class,
            client_kwargs=client_kwargs,
            enable_tracing=enable_tracing,
            trace_service_name=trace_service_name,
        )

        self._configs[name] = config
        tracing_status = "with tracing" if enable_tracing else "without tracing"
        logger.info(f"Registered service: {name} -> {base_url} ({tracing_status})")

    def register_client_type(
        self,
        service_name: str,
        client_class: type[BaseServiceClient],
        singleton: bool = True,
    ) -> None:
        """Register a custom client type for a service.

        Args:
            service_name: Name of the service
            client_class: Custom client class
            singleton: Whether to use singleton pattern
        """
        self._client_types[service_name] = client_class

        # Update existing config if present
        if service_name in self._configs:
            self._configs[service_name].client_class = client_class
            self._configs[service_name].singleton = singleton

        logger.info(f"Registered client type for {service_name}: {client_class.__name__}")

    def create_client(self, service_name: str, **kwargs: Any) -> Any:
        """Create a client instance for the service.

        Args:
            service_name: Name of the service
            **kwargs: Additional kwargs for client creation

        Returns:
            Client instance

        Raises:
            ValueError: If service is not registered
        """
        if service_name not in self._configs:
            raise ValueError(f"Service '{service_name}' not registered")

        config = self._configs[service_name]

        # Use custom client class if registered
        if service_name in self._client_types:
            client_class = self._client_types[service_name]
            # Check if it's a BaseServiceClient subclass
            if issubclass(client_class, BaseServiceClient):
                return client_class(config, **kwargs)
        else:
            # For non-BaseServiceClient classes (like httpx.AsyncClient)
            client_kwargs = {**config.client_kwargs, **kwargs}
            return config.client_class(
                base_url=config.base_url,
                timeout=config.timeout,
                headers=config.headers,
                **client_kwargs,
            )

    def get_dependency(self, service_name: str) -> Callable:
        """Get a dependency function for the service.

        Args:
            service_name: Name of the service

        Returns:
            Dependency function for use with FastAPI Depends()
        """
        if service_name not in self._configs:
            raise ValueError(f"Service '{service_name}' not registered")

        config = self._configs[service_name]

        if config.singleton:
            # Use singleton pattern
            def factory() -> Any:
                return self.create_client(service_name)

            # Register as singleton if not already done
            singleton_name = f"{service_name}_client"
            try:
                register_singleton(name=singleton_name, factory=factory)
            except Exception:
                # Already registered, that's fine
                pass

            return get_singleton(singleton_name)
        else:
            # Per-request instance
            def dependency() -> Any:
                return self.create_client(service_name)

            dependency.__name__ = f"get_{service_name}_client"
            dependency.__doc__ = f"Get {service_name} client instance"
            return dependency

    def list_services(self) -> dict[str, dict[str, Any]]:
        """List all registered services and their configurations.

        Returns:
            Dictionary mapping service names to their configurations
        """
        result = {}
        for name, config in self._configs.items():
            result[name] = {
                "base_url": config.base_url,
                "timeout": config.timeout,
                "singleton": config.singleton,
                "client_class": config.client_class.__name__,
                "custom_type": name in self._client_types,
            }
        return result

    async def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Perform health checks for all registered services.

        Returns:
            Dictionary mapping service names to health check results
        """
        results = {}
        for service_name in self._configs:
            try:
                client = self.create_client(service_name)
                if hasattr(client, "health_check"):
                    result = await client.health_check()
                else:
                    # Fallback for non-BaseServiceClient instances
                    result = await self._basic_health_check(service_name, client)
                results[service_name] = result
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                results[service_name] = {
                    "service": service_name,
                    "status": "error",
                    "error": str(e),
                }
        return results

    async def _basic_health_check(self, service_name: str, client: Any) -> dict[str, Any]:
        """Basic health check for generic HTTP clients.

        Args:
            service_name: Name of the service
            client: Client instance

        Returns:
            Health check result
        """
        try:
            if hasattr(client, "get"):
                response = await client.get("/health")
                return {
                    "service": service_name,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                }
            else:
                return {
                    "service": service_name,
                    "status": "unknown",
                    "message": "No health check method available",
                }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
            }


# Global service client factory instance
_service_factory = ServiceClientFactory()


def register_service(
    name: str,
    base_url: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
    singleton: bool = False,
    client_class: type | None = None,
    client_kwargs: dict[str, Any] | None = None,
    enable_tracing: bool = True,
    trace_service_name: str | None = None,
) -> None:
    """Register a service with the global factory.

    Args:
        name: Unique service name
        base_url: Service base URL
        timeout: Request timeout in seconds
        headers: Default headers
        singleton: Whether to use singleton pattern
        client_class: Custom client class
        client_kwargs: Additional client kwargs
        enable_tracing: Whether to enable automatic trace propagation
        trace_service_name: Service name for tracing (defaults to name)
    """
    _service_factory.register_service(
        name=name,
        base_url=base_url,
        timeout=timeout,
        headers=headers,
        singleton=singleton,
        client_class=client_class,
        client_kwargs=client_kwargs,
        enable_tracing=enable_tracing,
        trace_service_name=trace_service_name,
    )


def register_client_type(
    service_name: str,
    client_class: type[BaseServiceClient],
    singleton: bool = True,
) -> None:
    """Register a custom client type with the global factory.

    Args:
        service_name: Name of the service
        client_class: Custom client class
        singleton: Whether to use singleton pattern
    """
    _service_factory.register_client_type(service_name, client_class, singleton)


def get_service_client(service_name: str) -> Callable:
    """Get a dependency function for a service client.

    Args:
        service_name: Name of the service

    Returns:
        Dependency function for use with FastAPI Depends()
    """
    return _service_factory.get_dependency(service_name)


def create_service_client(service_name: str, **kwargs: Any) -> Any:
    """Create a service client instance.

    Args:
        service_name: Name of the service
        **kwargs: Additional kwargs for client creation

    Returns:
        Client instance
    """
    return _service_factory.create_client(service_name, **kwargs)


def list_services() -> dict[str, dict[str, Any]]:
    """List all registered services.

    Returns:
        Dictionary mapping service names to their configurations
    """
    return _service_factory.list_services()


async def health_check_all_services() -> dict[str, dict[str, Any]]:
    """Perform health checks for all services.

    Returns:
        Dictionary mapping service names to health check results
    """
    return await _service_factory.health_check_all()


def get_service_factory() -> ServiceClientFactory:
    """Get the global service factory instance.

    Returns:
        Global ServiceClientFactory instance
    """
    return _service_factory


# Convenience decorator for creating custom service clients
def service_client(
    service_name: str,
    singleton: bool = True,
) -> Callable[[type[BaseServiceClient]], type[BaseServiceClient]]:
    """Decorator to register a custom service client class.

    Args:
        service_name: Name of the service
        singleton: Whether to use singleton pattern

    Returns:
        Decorator function
    """

    def decorator(client_class: type[BaseServiceClient]) -> type[BaseServiceClient]:
        register_client_type(service_name, client_class, singleton)
        return client_class

    return decorator


# Export all public functions
__all__ = [
    "BaseServiceClient",
    "GenericServiceClient",
    "ServiceClientConfig",
    "ServiceClientFactory",
    "create_service_client",
    "get_service_client",
    "get_service_factory",
    "health_check_all_services",
    "list_services",
    "register_client_type",
    "register_service",
    "service_client",
]
