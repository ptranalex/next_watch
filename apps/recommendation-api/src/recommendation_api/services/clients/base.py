"""Base HTTP client for backend services."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, cast
from urllib.parse import urljoin

import httpx

from fast_core.errors import (
    ResourceNotFoundException,
    ValidationException,
    ExternalServiceException,
)

logger = logging.getLogger(__name__)


class BackendClientError(Exception):
    """Exception raised when backend API requests fail."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class BaseBackendClient:
    """Base HTTP client for backend API interactions."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """Initialize base client.

        Args:
            base_url: Base URL for the backend service (uses settings if None)
            timeout: Request timeout in seconds (uses settings if None)
        """
        ***REMOVED*** Backward compatibility: use settings if parameters not provided
        if base_url is None or timeout is None:
            from recommendation_api.config import settings

            self.base_url = (base_url or settings.backend_api_url).rstrip("/")
            self.timeout = timeout or settings.backend_api_timeout
        else:
            self.base_url = base_url.rstrip("/")
            self.timeout = timeout

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "RecommendationAPI/1.0",
        }
        self._client: Optional[httpx.AsyncClient] = None

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

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with enhanced error handling.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            ValidationException: For 400 Bad Request errors
            ResourceNotFoundException: For 404 Not Found errors
            ExternalServiceException: For other HTTP errors
            BackendClientError: For connection/timeout errors
        """
        client = await self._get_client()

        try:
            response = await client.request(
                method=method,
                url=urljoin(self.base_url, path),
                params=params,
                json=data,
                headers=headers or {},
            )

            ***REMOVED*** Handle HTTP status errors with semantic preservation
            if response.status_code >= 400:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", str(error_data))
                except Exception:
                    error_detail = response.text

                ***REMOVED*** Map HTTP status codes to semantic exceptions
                if response.status_code == 400:
                    raise ValidationException(f"Invalid request: {error_detail}")
                elif response.status_code == 404:
                    raise ResourceNotFoundException(
                        detail=f"Resource not found: {error_detail}",
                        resource_type="BackendResource",
                        resource_id=path,
                    )
                elif response.status_code >= 500:
                    logger.error(
                        f"Backend server error {response.status_code} for {method} {path}: {error_detail}"
                    )
                    raise ExternalServiceException(
                        f"Backend service error: {response.status_code} - {error_detail}"
                    )
                else:
                    logger.error(
                        f"Backend client error {response.status_code} for {method} {path}: {error_detail}"
                    )
                    raise ExternalServiceException(
                        f"Backend service returned error: {response.status_code} - {error_detail}"
                    )

            if response.headers.get("content-type", "").startswith("application/json"):
                json_response = response.json()
                ***REMOVED*** If the response is a list, wrap it in a dict for consistency
                if isinstance(json_response, list):
                    return {"data": json_response}
                return cast(Dict[str, Any], json_response)
            else:
                return {"data": response.text}

        except httpx.TimeoutException:
            error_msg = f"Backend API request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise BackendClientError(error_msg)
        except httpx.ConnectError:
            error_msg = f"Could not connect to Backend API at {self.base_url}"
            logger.error(error_msg)
            raise ExternalServiceException(error_msg)
        except (ValidationException, ResourceNotFoundException, ExternalServiceException):
            ***REMOVED*** Re-raise semantic exceptions without wrapping
            raise
        except Exception as e:
            error_msg = f"Unexpected error calling Backend API: {str(e)}"
            logger.error(error_msg)
            raise BackendClientError(error_msg)

    def _get_service_headers(self) -> Dict[str, str]:
        """Get headers for service-to-service authentication.

        Returns:
            Headers with authentication information
        """
        from recommendation_api.config import settings

        return {
            "X-API-Key": settings.internal_api_key,
            "X-Service-Name": "recommendation-api",
        }
