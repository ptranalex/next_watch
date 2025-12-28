"""Service client implementation for HTTP requests with versioning and configuration."""

import re
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class ServiceConfig:
    """Configuration for a service client.

    Args:
        base_url: Base URL of the service (e.g., "http://localhost:8000")
        version: API version (e.g., "v1", "v2", None for no version)
        api_prefix: API prefix (default: "api")
        timeout: Request timeout in seconds (default: 30)
        headers: Default headers to include with requests
    """

    base_url: str
    version: str | None = "v1"
    api_prefix: str = "api"
    timeout: float = 30.0
    headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.base_url:
            raise ValueError("base_url cannot be empty")
        if not self.api_prefix:
            raise ValueError("api_prefix cannot be empty")
        if self.version is not None and not self.version:
            raise ValueError("version must be a non-empty string or None")

        ***REMOVED*** Remove trailing slash from base_url for consistency
        self.base_url = self.base_url.rstrip("/")


class ServiceClient:
    """HTTP client for external services with automatic URL building and error handling.

    Provides a consistent interface for making HTTP requests to external services
    with automatic URL construction, versioning, and configuration management.

    Example:
        config = ServiceConfig("http://localhost:8000", version="v1")
        client = ServiceClient(config)

        ***REMOVED*** Makes request to: http://localhost:8000/api/v1/users/123
        response = await client.get("users/123")

        ***REMOVED*** Makes request to: http://localhost:8000/api/v1/movies
        response = await client.post("movies", json={"title": "Movie"})
    """

    def __init__(self, config: ServiceConfig):
        """Initialize service client with configuration.

        Args:
            config: Service configuration
        """
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=config.headers or {},
        )

    def _build_endpoint(self, path: str) -> str:
        """Build endpoint URL with API prefix and version.

        Args:
            path: Relative API path (e.g., "users/123", "/movies")

        Returns:
            Full endpoint path with prefix and version

        Examples:
            >>> client._build_endpoint("users/123")
            "/api/v1/users/123"
            >>> client._build_endpoint("/movies")
            "/api/v1/movies"
        """
        ***REMOVED*** Clean and normalize path
        clean_path = path.strip().lstrip("/")

        ***REMOVED*** Replace multiple consecutive slashes with single slash
        if clean_path:
            clean_path = re.sub(r"/+", "/", clean_path)

        ***REMOVED*** Build path components
        components = [self.config.api_prefix]
        if self.config.version:
            components.append(self.config.version)
        if clean_path:
            components.append(clean_path)

        ***REMOVED*** Join with single slashes and ensure leading slash
        return "/" + "/".join(components)

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make GET request to service endpoint.

        Args:
            path: Relative API path
            **kwargs: Additional arguments passed to httpx.get()

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            httpx.RequestError: If request cannot be made
        """
        endpoint = self._build_endpoint(path)
        response = await self._client.get(endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make POST request to service endpoint.

        Args:
            path: Relative API path
            **kwargs: Additional arguments passed to httpx.post()

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            httpx.RequestError: If request cannot be made
        """
        endpoint = self._build_endpoint(path)
        response = await self._client.post(endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make PUT request to service endpoint.

        Args:
            path: Relative API path
            **kwargs: Additional arguments passed to httpx.put()

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            httpx.RequestError: If request cannot be made
        """
        endpoint = self._build_endpoint(path)
        response = await self._client.put(endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make PATCH request to service endpoint.

        Args:
            path: Relative API path
            **kwargs: Additional arguments passed to httpx.patch()

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            httpx.RequestError: If request cannot be made
        """
        endpoint = self._build_endpoint(path)
        response = await self._client.patch(endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make DELETE request to service endpoint.

        Args:
            path: Relative API path
            **kwargs: Additional arguments passed to httpx.delete()

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            httpx.RequestError: If request cannot be made
        """
        endpoint = self._build_endpoint(path)
        response = await self._client.delete(endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Make HTTP request with specified method to service endpoint.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
            path: Relative API path
            **kwargs: Additional arguments passed to httpx.request()

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            httpx.RequestError: If request cannot be made
        """
        endpoint = self._build_endpoint(path)
        response = await self._client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "ServiceClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
