"""Service client factory for HTTP client lifecycle management.

Provides enterprise-grade HTTP client management with connection pooling,
retry policies, and proper resource cleanup based on BFF API CLI patterns.
"""

import asyncio
from typing import Any, Dict, Optional, cast

import httpx
import redis.asyncio as redis
from redis.asyncio import Redis
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .service_registry import ServiceConfig, ServiceRegistry

logger = structlog.get_logger(__name__)


class ServiceClientError(Exception):
    """Base exception for service client errors."""

    pass


class ServiceClientFactory:
    """Factory for creating and managing service clients with enterprise patterns.

    Provides:
    - HTTP client lifecycle management with connection pooling
    - Retry policies with exponential backoff
    - Proper resource cleanup
    - Service-specific configuration
    """

    def __init__(self, registry: Optional[ServiceRegistry] = None):
        """Initialize service client factory.

        Args:
            registry: Service registry for configuration lookup
        """
        self.registry = registry or ServiceRegistry()
        self._http_clients: Dict[str, httpx.AsyncClient] = {}
        self._redis_clients: Dict[str, Redis] = {}
        self.logger = logger.bind(component="client_factory")

    async def get_http_client(self, service_name: str) -> httpx.AsyncClient:
        """Get or create HTTP client for a service.

        Args:
            service_name: Name of the service

        Returns:
            Configured HTTP client

        Raises:
            ServiceClientError: If service not found or client creation fails
        """
        if service_name in self._http_clients:
            return self._http_clients[service_name]

        try:
            service_config = self.registry.get_service(service_name)
        except KeyError as e:
            raise ServiceClientError(
                f"Service '{service_name}' not found in registry"
            ) from e

        if service_config.service_type != "http":
            raise ServiceClientError(
                f"Service '{service_name}' is not an HTTP service (type: {service_config.service_type})"
            )

        ***REMOVED*** Create HTTP client with enterprise configuration
        client = httpx.AsyncClient(
            base_url=service_config.base_url,
            timeout=httpx.Timeout(service_config.timeout),
            limits=httpx.Limits(
                max_connections=20,  ***REMOVED*** Connection pool size
                max_keepalive_connections=10,
            ),
            headers={
                "User-Agent": "NextWatch-CLI-Framework/0.1.0",
                "Accept": "application/json",
                **service_config.headers,
            },
        )

        self._http_clients[service_name] = client

        self.logger.info(
            "HTTP client created",
            service_name=service_name,
            base_url=service_config.base_url,
            timeout=service_config.timeout,
        )

        return client

    async def get_redis_client(self, service_name: str) -> Redis:
        """Get or create Redis client for a service.

        Args:
            service_name: Name of the Redis service

        Returns:
            Configured Redis client

        Raises:
            ServiceClientError: If service not found or client creation fails
        """
        if service_name in self._redis_clients:
            return self._redis_clients[service_name]

        try:
            service_config = self.registry.get_service(service_name)
        except KeyError as e:
            raise ServiceClientError(
                f"Service '{service_name}' not found in registry"
            ) from e

        if service_config.service_type != "redis":
            raise ServiceClientError(
                f"Service '{service_name}' is not a Redis service (type: {service_config.service_type})"
            )

        ***REMOVED*** Create Redis client with timeout configuration
        client = cast(
            Redis,
            redis.Redis.from_url(
                service_config.url,
                socket_timeout=service_config.timeout,
                socket_connect_timeout=service_config.timeout,
                decode_responses=True,
            ),
        )

        self._redis_clients[service_name] = client

        self.logger.info(
            "Redis client created",
            service_name=service_name,
            url=service_config.url,
            timeout=service_config.timeout,
        )

        return client

    async def make_request(
        self,
        service_name: str,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with retry logic.

        Args:
            service_name: Name of the service
            method: HTTP method
            path: Request path
            **kwargs: Additional arguments for httpx request

        Returns:
            HTTP response

        Raises:
            ServiceClientError: If request fails after retries
        """
        client = await self.get_http_client(service_name)
        service_config = self.registry.get_service(service_name)

        ***REMOVED*** Create retry decorator based on service configuration
        if service_config.retry_attempts > 0:
            if service_config.retry_backoff == "exponential":
                wait_strategy = wait_exponential(multiplier=1, min=1, max=10)
            elif service_config.retry_backoff == "linear":
                wait_strategy = wait_exponential(multiplier=1, min=1, max=1)
            else:  ***REMOVED*** fixed
                wait_strategy = wait_exponential(multiplier=0, min=2, max=2)

            @retry(
                stop=stop_after_attempt(service_config.retry_attempts + 1),
                wait=wait_strategy,
                retry=retry_if_exception_type(
                    (httpx.RequestError, httpx.HTTPStatusError)
                ),
                reraise=True,
            )
            async def _make_request_with_retry() -> httpx.Response:
                try:
                    response = await client.request(method, path, **kwargs)
                    response.raise_for_status()
                    return response
                except httpx.HTTPStatusError as e:
                    self.logger.warning(
                        "HTTP error",
                        service_name=service_name,
                        method=method,
                        path=path,
                        status_code=e.response.status_code,
                        error=str(e),
                    )
                    raise
                except httpx.RequestError as e:
                    self.logger.warning(
                        "Request error",
                        service_name=service_name,
                        method=method,
                        path=path,
                        error=str(e),
                    )
                    raise

            try:
                return await _make_request_with_retry()
            except Exception as e:
                raise ServiceClientError(
                    f"Request to {service_name} failed after {service_config.retry_attempts} retries: {e}"
                ) from e

        else:
            ***REMOVED*** No retries - single attempt
            try:
                response = await client.request(method, path, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                raise ServiceClientError(
                    f"Request to {service_name} failed: {e}"
                ) from e

    async def close_service(self, service_name: str) -> None:
        """Close clients for a specific service.

        Args:
            service_name: Name of the service to close
        """
        ***REMOVED*** Close HTTP client if exists
        if service_name in self._http_clients:
            await self._http_clients[service_name].aclose()
            del self._http_clients[service_name]
            self.logger.info("HTTP client closed", service_name=service_name)

        ***REMOVED*** Close Redis client if exists
        if service_name in self._redis_clients:
            await self._redis_clients[service_name].close()
            del self._redis_clients[service_name]
            self.logger.info("Redis client closed", service_name=service_name)

    async def close_all(self) -> None:
        """Close all clients and clean up resources."""
        ***REMOVED*** Close all HTTP clients
        for service_name, client in self._http_clients.items():
            try:
                await client.aclose()
                self.logger.info("HTTP client closed", service_name=service_name)
            except Exception as e:
                self.logger.error(
                    "Error closing HTTP client", service_name=service_name, error=str(e)
                )

        ***REMOVED*** Close all Redis clients
        for service_name, redis_client in self._redis_clients.items():
            try:
                await redis_client.close()
                self.logger.info("Redis client closed", service_name=service_name)
            except Exception as e:
                self.logger.error(
                    "Error closing Redis client",
                    service_name=service_name,
                    error=str(e),
                )

        ***REMOVED*** Clear client dictionaries
        self._http_clients.clear()
        self._redis_clients.clear()

        self.logger.info("All service clients closed")

    async def __aenter__(self) -> "ServiceClientFactory":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with cleanup."""
        await self.close_all()

    def __len__(self) -> int:
        """Return total number of active clients."""
        return len(self._http_clients) + len(self._redis_clients)

    def __repr__(self) -> str:
        """String representation of the factory."""
        return (
            f"ServiceClientFactory("
            f"http_clients={list(self._http_clients.keys())}, "
            f"redis_clients={list(self._redis_clients.keys())}"
            f")"
        )
