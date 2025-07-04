"""Base HTTP client for backend API communication."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from fast_core.dependencies.client_factory import BaseServiceClient, ServiceClientConfig
from fast_core.errors import (
    handle_service_error,
    service_error_handler,
)

from bff_api.config.app import BFFAPIConfig, settings

logger = get_logger(__name__)


class BackendClientError(Exception):
    """Base exception for backend client errors."""

    pass


class BackendClientTransientError(BackendClientError):
    """Transient error that can be retried (network issues, 5xx errors)."""

    pass


class BackendClientPermanentError(BackendClientError):
    """Permanent error that should not be retried (4xx errors)."""

    pass


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

    ***REMOVED*** Remove the _get_client override - use Fast Core's implementation
    ***REMOVED*** Fast Core already handles headers from config properly

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
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(BackendClientTransientError),
    )
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
            BackendClientError: For service errors
        """
        client = await self._get_client()

        ***REMOVED*** Use Fast Core's header management with trace propagation
        request_headers = self._get_request_headers(headers)

        try:
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=data,
                headers=request_headers,
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

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            ***REMOVED*** 4xx errors are permanent (don't retry)
            if 400 <= status_code < 500:
                ***REMOVED*** Log 4xx as appropriate levels
                if status_code == 401:
                    logger.debug(f"Authentication failed for {method} {path}: {status_code}")
                elif status_code == 404:
                    logger.debug(f"Resource not found for {method} {path}: {status_code}")
                else:
                    logger.info(f"Client error {status_code} for {method} {path}")
                raise BackendClientPermanentError(f"Backend service error: {status_code}")
            ***REMOVED*** 5xx errors are transient (can retry)
            else:
                logger.error(f"Server error {status_code} for {method} {path}: {e}")
                raise BackendClientTransientError(f"Backend service error: {status_code}")

        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {path}: {e}")
            ***REMOVED*** Network errors are transient (can retry)
            raise BackendClientTransientError(f"Backend service request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {path}: {e}")
            ***REMOVED*** Unexpected errors are treated as permanent
            raise BackendClientPermanentError(f"Unexpected backend error: {e}")

    def _get_auth_headers(self, user_id: int) -> Dict[str, str]:
        """Get service-to-service authentication headers.

        Args:
            user_id: User ID for authentication context

        Returns:
            Authentication headers including service auth and user context
        """
        headers = {
            "X-User-ID": str(user_id),
            "X-Service": "bff-api",
        }

        ***REMOVED*** Include Authorization header from service client config if available
        if self.config.headers and "Authorization" in self.config.headers:
            auth_header = self.config.headers["Authorization"]
            headers["Authorization"] = auth_header
            ***REMOVED*** Mask the token for security but show first/last few chars for debugging
            masked_auth = (
                f"{auth_header[:12]}...{auth_header[-4:]}" if len(auth_header) > 16 else "***"
            )
            logger.debug(f"Using Authorization header: {masked_auth}")
        else:
            logger.warning(
                f"No Authorization header in config! Config headers: {self.config.headers}"
            )

        return headers

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
