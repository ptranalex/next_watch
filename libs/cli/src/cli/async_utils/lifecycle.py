"""Service lifecycle management for proper async resource cleanup.

Provides ServiceLifecycleManager for managing multiple service clients with
proper cleanup, following the patterns from BFF API CLI where multiple services
need coordinated lifecycle management.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, AsyncContextManager
import structlog
from contextlib import AsyncExitStack

from ..services.client_factory import ServiceClientFactory

logger = structlog.get_logger(__name__)


class ServiceLifecycleManager:
    """Manager for coordinating lifecycle of multiple service clients.

    Provides coordinated startup and cleanup for multiple services, ensuring
    proper resource cleanup even when operations fail. Based on patterns from
    BFF API CLI where multiple service clients need proper coordination.

    Example:
        >>> async with ServiceLifecycleManager() as manager:
        ...     await manager.register_service("backend", backend_config)
        ...     await manager.register_service("auth", auth_config)
        ...     ***REMOVED*** Use services
        ...     backend_client = await manager.get_client("backend")
        ... ***REMOVED*** All services automatically cleaned up
    """

    def __init__(self) -> None:
        """Initialize the lifecycle manager."""
        self._factories: Dict[str, ServiceClientFactory] = {}
        self._cleanup_stack: Optional[AsyncExitStack] = None
        self._services: Dict[str, Any] = {}
        self.logger = logger.bind(component="lifecycle_manager")

    async def register_service(self, name: str, factory: ServiceClientFactory) -> None:
        """Register a service factory for managed lifecycle.

        Args:
            name: Service name for lookup
            factory: Service client factory
        """
        if self._cleanup_stack is None:
            raise RuntimeError(
                "ServiceLifecycleManager not properly initialized. Use 'async with' pattern."
            )

        self._factories[name] = factory

        ***REMOVED*** Add factory to cleanup stack
        await self._cleanup_stack.enter_async_context(factory)

        self.logger.info("Service registered", service_name=name)

    async def get_client(self, service_name: str, client_type: str = "http") -> Any:
        """Get a client for a registered service.

        Args:
            service_name: Name of the registered service
            client_type: Type of client ("http" or "redis")

        Returns:
            Service client instance

        Raises:
            KeyError: If service not registered
            ValueError: If invalid client type
        """
        if service_name not in self._factories:
            raise KeyError(f"Service '{service_name}' not registered")

        factory = self._factories[service_name]

        if client_type == "http":
            return await factory.get_http_client(service_name)
        elif client_type == "redis":
            return await factory.get_redis_client(service_name)
        else:
            raise ValueError(f"Invalid client type: {client_type}")

    async def get_all_clients(self, client_type: str = "http") -> Dict[str, Any]:
        """Get clients for all registered services.

        Args:
            client_type: Type of clients to get

        Returns:
            Dictionary mapping service names to client instances
        """
        clients = {}
        for service_name in self._factories:
            try:
                clients[service_name] = await self.get_client(service_name, client_type)
            except Exception as e:
                self.logger.warning(
                    "Failed to get client",
                    service_name=service_name,
                    client_type=client_type,
                    error=str(e),
                )

        return clients

    async def close_service(self, service_name: str) -> None:
        """Close a specific service early.

        Args:
            service_name: Name of service to close
        """
        if service_name in self._factories:
            factory = self._factories[service_name]
            await factory.close_service(service_name)
            self.logger.info("Service closed early", service_name=service_name)

    def get_registered_services(self) -> List[str]:
        """Get list of registered service names.

        Returns:
            List of service names
        """
        return list(self._factories.keys())

    async def __aenter__(self) -> "ServiceLifecycleManager":
        """Async context manager entry."""
        self._cleanup_stack = AsyncExitStack()
        await self._cleanup_stack.__aenter__()
        self.logger.info("ServiceLifecycleManager initialized")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with cleanup."""
        if self._cleanup_stack:
            try:
                await self._cleanup_stack.__aexit__(exc_type, exc_val, exc_tb)
                self.logger.info("All services cleaned up successfully")
            except Exception as e:
                self.logger.error("Error during service cleanup", error=str(e))
                raise
            finally:
                self._cleanup_stack = None
                self._factories.clear()
                self._services.clear()


class ManagedService:
    """A service wrapper that ensures proper cleanup.

    Can be used to wrap any service that needs cleanup, providing a consistent
    interface for lifecycle management.
    """

    def __init__(self, service: Any, name: str, cleanup_method: str = "close"):
        """Initialize managed service.

        Args:
            service: The service instance to manage
            name: Name of the service for logging
            cleanup_method: Name of the cleanup method to call
        """
        self.service = service
        self.name = name
        self.cleanup_method = cleanup_method
        self.logger = logger.bind(service_name=name)

    async def cleanup(self) -> None:
        """Perform cleanup on the managed service."""
        try:
            if hasattr(self.service, self.cleanup_method):
                cleanup_fn = getattr(self.service, self.cleanup_method)
                if asyncio.iscoroutinefunction(cleanup_fn):
                    await cleanup_fn()
                else:
                    cleanup_fn()
                self.logger.info("Service cleanup completed")
            else:
                self.logger.warning(
                    "Service does not have cleanup method",
                    cleanup_method=self.cleanup_method,
                )
        except Exception as e:
            self.logger.error("Service cleanup failed", error=str(e))
            raise

    async def __aenter__(self) -> Any:
        """Return the wrapped service."""
        self.logger.info("Service acquired")
        return self.service

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup the service."""
        await self.cleanup()


def managed_service(
    service: Any, name: str, cleanup_method: str = "close"
) -> AsyncContextManager[Any]:
    """Create a managed service context manager.

    Args:
        service: Service to manage
        name: Service name for logging
        cleanup_method: Name of cleanup method

    Returns:
        Async context manager for the service

    Example:
        >>> async with managed_service(my_client, "backend", "close") as client:
        ...     await client.do_something()
        ... ***REMOVED*** client.close() called automatically
    """
    return ManagedService(service, name, cleanup_method)
