"""Service client dependencies for FastAPI applications.

This module provides dependency injection utilities for HTTP service clients,
enabling clean service-to-service communication patterns.
"""

from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from config.logging import get_logger
from fastapi import Depends, HTTPException, Request

logger = get_logger(__name__)


def get_app_settings(request: Request) -> Any:
    """Get application settings from request state.

    Args:
        request: FastAPI request object

    Returns:
        Application settings object
    """
    return getattr(request.app.state, "settings", None)


def create_service_client(base_url: str, timeout: int = 30) -> httpx.AsyncClient:
    """Create an HTTP client for service communication.

    Args:
        base_url: Base URL for the service
        timeout: Request timeout in seconds

    Returns:
        Configured HTTP client
    """
    return httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(timeout),
        headers={
            "User-Agent": "fast-core-service-client/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )


def get_service_client_factory(service_name: str) -> Callable[..., Awaitable[httpx.AsyncClient]]:
    """Create a dependency factory for a specific service client.

    Args:
        service_name: Name of the service (e.g., 'backend', 'auth')

    Returns:
        Dependency function that returns configured HTTP client
    """

    async def service_client_dependency(
        settings: Any = Depends(get_app_settings),
    ) -> httpx.AsyncClient:
        """Get HTTP client for specific service.

        Args:
            settings: Application settings

        Returns:
            Configured HTTP client for the service

        Raises:
            HTTPException: If service URL is not configured
        """
        if not settings:
            raise HTTPException(status_code=500, detail="Application settings not available")

        ***REMOVED*** Get service URL
        service_url = None
        if hasattr(settings, "get_service_url"):
            service_url = settings.get_service_url(service_name)
        elif hasattr(settings, "service_urls"):
            service_url = settings.service_urls.get(service_name)

        if not service_url:
            raise HTTPException(
                status_code=500, detail=f"Service URL for '{service_name}' not configured"
            )

        ***REMOVED*** Get service timeout
        timeout = 30  ***REMOVED*** default
        if hasattr(settings, "get_service_timeout"):
            timeout = settings.get_service_timeout(service_name, 30)
        elif hasattr(settings, "service_timeouts"):
            timeout = settings.service_timeouts.get(service_name, 30)

        logger.debug(f"Creating {service_name} client: {service_url} (timeout: {timeout}s)")
        return create_service_client(service_url, timeout)

    return service_client_dependency


***REMOVED*** Pre-configured dependency functions for common services
get_backend_client = get_service_client_factory("backend")
get_auth_client = get_service_client_factory("auth")
get_recommendation_client = get_service_client_factory("recommendation")
get_ml_client = get_service_client_factory("ml")


def get_generic_http_client() -> httpx.AsyncClient:
    """Get a generic HTTP client for general use.

    Returns:
        Generic HTTP client
    """
    return httpx.AsyncClient(
        timeout=httpx.Timeout(30),
        headers={
            "User-Agent": "fast-core-http-client/1.0",
            "Accept": "application/json",
        },
    )
