"""Base HTTP client for backend API communication."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential
from fast_core.dependencies.client_factory import BaseServiceClient, ServiceClientConfig
from fast_core.errors import (
    handle_service_error,
    service_error_handler,
)

from bff_api.config.app import BFFAPIConfig, settings

logger = get_logger(__name__)


class BaseBackendClient(BaseServiceClient):
    """Base HTTP client for communicating with backend API.

    Now inherits from Fast Core's BaseServiceClient for better integration,
    singleton support, and automatic health checking with proper error handling.
    """

    def __init__(
        self, config: ServiceClientConfig, bff_config: Optional[BFFAPIConfig] = None
    ) -> None:
        """Initialize backend client.

        Args:
            config: Service client configuration from Fast Core
            bff_config: BFF-specific configuration (optional, uses global settings if not provided)
        """
        super().__init__(config)
        self.bff_config = bff_config or settings
        self.timeout = config.timeout
        self.service_name = "backend-api"  ***REMOVED*** For error handling

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with BFF-specific headers."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "NextWatch-BFF/0.1.0",
                    "Accept": "application/json",
                    **self.config.headers,  ***REMOVED*** Include any additional headers from config
                },
                **self.config.client_kwargs,
            )
        return self._client

    def _build_api_path(self, path: str) -> str:
        """Build API path with version prefix.

        Args:
            path: Relative API path

        Returns:
            Full API path with version prefix
        """
        ***REMOVED*** Remove leading slash if present to avoid double slashes
        clean_path = path.lstrip("/")
        return f"/api/v1/{clean_path}"

    @service_error_handler("backend-api", logger)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and Fast Core error handling.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            ExternalServiceException: For service errors (handled by decorator)
        """
        client = await self._get_client()

        response = await client.request(
            method=method,
            url=path,
            params=params,
            json=data,
            headers=headers or {},
        )
        response.raise_for_status()

        if response.headers.get("content-type", "").startswith("application/json"):
            json_response = response.json()
            ***REMOVED*** If the response is a list, wrap it in a dict for consistency
            if isinstance(json_response, list):
                return {"data": json_response}
            return cast(Dict[str, Any], json_response)
        else:
            return {"data": response.text}

    def _get_auth_headers(self, user_id: int) -> Dict[str, str]:
        """Get service-to-service authentication headers.

        Args:
            user_id: User ID for authentication context

        Returns:
            Authentication headers
        """
        ***REMOVED*** TODO: Implement proper service-to-service authentication
        ***REMOVED*** For now, just pass user context
        return {
            "X-User-ID": str(user_id),
            "X-Service": "bff-api",
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check against backend API.

        Returns:
            Health check result with service status
        """
        try:
            response = await self._make_request("GET", "/health")
            return {
                "service": self.service_name,
                "status": "healthy",
                "url": self.base_url,
                "backend_status": response.get("status", "unknown"),
            }
        except Exception as e:
            logger.warning(f"Health check failed for {self.service_name}: {e}")
            return {
                "service": self.service_name,
                "status": "unhealthy",
                "url": self.base_url,
                "error": str(e),
            }
