"""Service Client Factory for Fast Core.

This module provides a flexible factory system for creating and managing
service clients with support for custom client types, singleton patterns,
and automatic configuration.
"""

import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, get_type_hints
from abc import ABC, abstractmethod

import httpx
from fastapi import Depends
from config.logging import get_logger

from .singleton import get_singleton_client, register_singleton, get_singleton

***REMOVED*** Import tracing functionality
try:
    from fast_core.middleware.context import get_request_context, inject_trace_context

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
        headers: Optional[Dict[str, str]] = None,
        singleton: bool = False,
        client_class: Optional[Type] = None,
        client_kwargs: Optional[Dict[str, Any]] = None,
        enable_tracing: bool = True,
        trace_service_name: Optional[str] = None,
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
        self._client: Optional[httpx.AsyncClient] = None

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
        self, additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Get headers for current request with automatic trace injection.

        Args:
            additional_headers: Additional headers to include

        Returns:
            Headers dictionary with trace context injected
        """
        ***REMOVED*** Start with base headers from config
        headers = dict(self.config.headers)

        ***REMOVED*** Add any additional headers provided
        if additional_headers:
            headers.update(additional_headers)

        ***REMOVED*** Add automatic trace headers if tracing is enabled
        if self.config.enable_tracing and TRACING_AVAILABLE:
            try:
                context = get_request_context()
                if context:
                    ***REMOVED*** Inject trace propagation headers
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
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the service."""
        pass


class GenericServiceClient(BaseServiceClient):
    """Generic service client for simple HTTP operations."""

    async def health_check(self) -> Dict[str, Any]:
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
        ***REMOVED*** Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.get(path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make POST request with automatic trace header injection."""
        client = await self._get_client()
        ***REMOVED*** Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.post(path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make PUT request with automatic trace header injection."""
        client = await self._get_client()
        ***REMOVED*** Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make DELETE request with automatic trace header injection."""
        client = await self._get_client()
        ***REMOVED*** Inject trace headers into request headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers
        return await client.delete(path, **kwargs)


class ServiceClientFactory:
    """Factory for creating and managing service clients."""

    def __init__(self) -> None:
        """Initialize service client factory."""
        self._configs: Dict[str, ServiceClientConfig] = {}
        self._client_types: Dict[str, Type[BaseServiceClient]] = {}
        self._instances: Dict[str, Any] = {}

    def register_service(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        singleton: bool = False,
        client_class: Optional[Type] = None,
        client_kwargs: Optional[Dict[str, Any]] = None,
        enable_tracing: bool = True,
        trace_service_name: Optional[str] = None,
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
        client_class: Type[BaseServiceClient],
        singleton: bool = True,
    ) -> None:
        """Register a custom client type for a service.

        Args:
            service_name: Name of the service
            client_class: Custom client class
            singleton: Whether to use singleton pattern
        """
        self._client_types[service_name] = client_class

        ***REMOVED*** Update existing config if present
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

        ***REMOVED*** Use custom client class if registered
        if service_name in self._client_types:
            client_class = self._client_types[service_name]
            ***REMOVED*** Check if it's a BaseServiceClient subclass
            if issubclass(client_class, BaseServiceClient):
                return client_class(config, **kwargs)
        else:
            ***REMOVED*** For non-BaseServiceClient classes (like httpx.AsyncClient)
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
            ***REMOVED*** Use singleton pattern
            def factory() -> Any:
                return self.create_client(service_name)

            ***REMOVED*** Register as singleton if not already done
            singleton_name = f"{service_name}_client"
            try:
                register_singleton(name=singleton_name, factory=factory)
            except Exception:
                ***REMOVED*** Already registered, that's fine
                pass

            return get_singleton(singleton_name)
        else:
            ***REMOVED*** Per-request instance
            def dependency() -> Any:
                return self.create_client(service_name)

            dependency.__name__ = f"get_{service_name}_client"
            dependency.__doc__ = f"Get {service_name} client instance"
            return dependency

    def list_services(self) -> Dict[str, Dict[str, Any]]:
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

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
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
                    ***REMOVED*** Fallback for non-BaseServiceClient instances
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

    async def _basic_health_check(self, service_name: str, client: Any) -> Dict[str, Any]:
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


***REMOVED*** Global service client factory instance
_service_factory = ServiceClientFactory()


def register_service(
    name: str,
    base_url: str,
    timeout: int = 30,
    headers: Optional[Dict[str, str]] = None,
    singleton: bool = False,
    client_class: Optional[Type] = None,
    client_kwargs: Optional[Dict[str, Any]] = None,
    enable_tracing: bool = True,
    trace_service_name: Optional[str] = None,
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
    client_class: Type[BaseServiceClient],
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


def list_services() -> Dict[str, Dict[str, Any]]:
    """List all registered services.

    Returns:
        Dictionary mapping service names to their configurations
    """
    return _service_factory.list_services()


async def health_check_all_services() -> Dict[str, Dict[str, Any]]:
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


***REMOVED*** Convenience decorator for creating custom service clients
def service_client(
    service_name: str,
    singleton: bool = True,
) -> Callable[[Type[BaseServiceClient]], Type[BaseServiceClient]]:
    """Decorator to register a custom service client class.

    Args:
        service_name: Name of the service
        singleton: Whether to use singleton pattern

    Returns:
        Decorator function
    """

    def decorator(client_class: Type[BaseServiceClient]) -> Type[BaseServiceClient]:
        register_client_type(service_name, client_class, singleton)
        return client_class

    return decorator


***REMOVED*** Export all public functions
__all__ = [
    "ServiceClientConfig",
    "BaseServiceClient",
    "GenericServiceClient",
    "ServiceClientFactory",
    "register_service",
    "register_client_type",
    "get_service_client",
    "create_service_client",
    "list_services",
    "health_check_all_services",
    "get_service_factory",
    "service_client",
]
