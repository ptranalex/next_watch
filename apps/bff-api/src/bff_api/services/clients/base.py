"""Base HTTP client for backend API communication."""

import time
from typing import Any, cast

import httpx
from config.logging import get_logger
from fast_core.dependencies.client_factory import BaseServiceClient, ServiceClientConfig
from fast_core.errors import (
    service_error_handler,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bff_api.config.app import BFFAPIConfig, settings
from bff_api.core.metrics import get_bff_metrics

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

    def __init__(self, config: ServiceClientConfig, bff_config: BFFAPIConfig | None = None) -> None:
        """Initialize backend client.

        Args:
            config: Service client configuration from Fast Core
            bff_config: BFF-specific configuration (optional, uses global settings if not provided)
        """
        super().__init__(config)
        self.bff_config = bff_config or settings
        self.timeout = config.timeout
        self.service_name = "backend-api"  # For error handling

    # Remove the _get_client override - use Fast Core's implementation
    # Fast Core already handles headers from config properly

    def _build_api_path(self, path: str) -> str:
        """Build API path with version prefix.

        Args:
            path: Relative API path

        Returns:
            Full API path with version prefix
        """
        # Remove leading slash if present to avoid double slashes
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
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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
        start_time = time.time()
        metrics = get_bff_metrics()

        client = await self._get_client()

        # Use Fast Core's header management with trace propagation
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

            # Record successful service call metrics
            response_time = time.time() - start_time
            if metrics:
                metrics.record_service_call(
                    service_name=self.service_name,
                    endpoint=path,
                    status="success",
                    response_time=response_time,
                )

            if response.headers.get("content-type", "").startswith("application/json"):
                json_response = response.json()
                # If the response is a list, wrap it in a dict for consistency
                if isinstance(json_response, list):
                    return {"data": json_response}
                return cast(dict[str, Any], json_response)
            else:
                return {"data": response.text}

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            response_time = time.time() - start_time

            # Record error metrics
            if metrics:
                error_status = "rate_limit" if status_code == 429 else "http_error"
                metrics.record_service_call(
                    service_name=self.service_name,
                    endpoint=path,
                    status=error_status,
                    response_time=response_time,
                )
                metrics.record_service_error(
                    service_name=self.service_name, error_type=f"http_{status_code}"
                )

            # 429 Too Many Requests should be retried with backoff
            if status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait_seconds = int(retry_after)
                        logger.warning(
                            f"Rate limited by {method} {path}, will retry after {wait_seconds}s",
                            status_code=status_code,
                            retry_after=wait_seconds,
                            service=self.service_name,
                        )
                    except ValueError:
                        logger.warning(f"Invalid Retry-After header: {retry_after}")
                else:
                    logger.warning(
                        f"Rate limited by {method} {path}, no Retry-After header provided",
                        status_code=status_code,
                        service=self.service_name,
                    )
                # Treat 429 as transient error for retry
                raise BackendClientTransientError(f"Rate limited by service: {status_code}")

            # Other 4xx errors are permanent (don't retry)
            elif 400 <= status_code < 500:
                # Log 4xx as appropriate levels
                if status_code == 401:
                    logger.debug(f"Authentication failed for {method} {path}: {status_code}")
                elif status_code == 404:
                    logger.debug(f"Resource not found for {method} {path}: {status_code}")
                else:
                    logger.warning(f"Client error {status_code} for {method} {path}")
                raise BackendClientPermanentError(f"Backend service error: {status_code}")
            # 5xx errors are transient (can retry)
            else:
                logger.error(
                    f"Server error {status_code} for {method} {path}: {e}",
                    exc_info=True,
                )
                raise BackendClientTransientError(f"Backend service error: {status_code}")

        except httpx.RequestError as e:
            response_time = time.time() - start_time

            # Record network error metrics
            if metrics:
                error_type = "timeout" if "timeout" in str(e).lower() else "connection"
                metrics.record_service_call(
                    service_name=self.service_name,
                    endpoint=path,
                    status=error_type,
                    response_time=response_time,
                )
                metrics.record_service_error(service_name=self.service_name, error_type=error_type)

            logger.error(f"Request error for {method} {path}: {e}", exc_info=True)
            # Network errors are transient (can retry)
            raise BackendClientTransientError(f"Backend service request failed: {e}")
        except Exception as e:
            response_time = time.time() - start_time

            # Record unexpected error metrics
            if metrics:
                metrics.record_service_call(
                    service_name=self.service_name,
                    endpoint=path,
                    status="error",
                    response_time=response_time,
                )
                metrics.record_service_error(
                    service_name=self.service_name, error_type="unexpected"
                )

            logger.error(f"Unexpected error for {method} {path}: {e}", exc_info=True)
            # Unexpected errors are treated as permanent
            raise BackendClientPermanentError(f"Unexpected backend error: {e}")

    def _get_auth_headers(self, user_id: int) -> dict[str, str]:
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

        # Include Authorization header from service client config if available
        if self.config.headers and "Authorization" in self.config.headers:
            auth_header = self.config.headers["Authorization"]
            headers["Authorization"] = auth_header
            # Mask the token for security but show first/last few chars for debugging
            masked_auth = (
                f"{auth_header[:12]}...{auth_header[-4:]}" if len(auth_header) > 16 else "***"
            )
            logger.debug(f"Using Authorization header: {masked_auth}")
        else:
            # Warn without echoing full headers structure to avoid secrets in logs
            logger.warning("No Authorization header in config for backend client")

        return headers

    async def health_check(self) -> dict[str, Any]:
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
