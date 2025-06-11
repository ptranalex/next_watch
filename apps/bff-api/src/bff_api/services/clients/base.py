"""Base HTTP client for backend API communication."""

import logging
from typing import Dict, List, Optional, Any, Union, cast
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from bff_api.config.app import Config

logger = logging.getLogger(__name__)


class BackendClientError(Exception):
    """Base exception for backend client errors."""

    pass


class BaseBackendClient:
    """Base HTTP client for communicating with backend API."""

    def __init__(self, config: Config):
        """Initialize backend client.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.base_url = config.backend_api_url
        self.timeout = config.backend_api_timeout
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
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "NextWatch-BFF/0.1.0",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            BackendClientError: If request fails
        """
        client = await self._get_client()

        try:
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

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {method} {path}: {e}")
            raise BackendClientError(f"Backend API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {path}: {e}")
            raise BackendClientError(f"Backend API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {path}: {e}")
            raise BackendClientError(f"Unexpected backend error: {e}")

    def _get_auth_headers(self, user_id: int) -> Dict[str, str]:
        """Get service-to-service authentication headers.

        Args:
            user_id: User ID to pass via X-User-ID header

        Returns:
            Authentication headers for backend API
        """
        return {
            "Authorization": f"Bearer {self.config.internal_api_key or 'bff-to-backend-secret-key'}",
            "X-User-ID": str(user_id),
        }
