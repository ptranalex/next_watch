"""Authentication client for communicating with auth service."""

import logging
from typing import Dict, Any, Optional, TypeVar, cast

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from bff_api.config.app import Config

logger = logging.getLogger(__name__)


class AuthClientError(Exception):
    """Base exception for auth client errors."""

    pass


class AuthClient:
    """HTTP client for communicating with authentication service."""

    def __init__(self, config: Config):
        """Initialize auth client.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.base_url = config.auth_api_url
        self.timeout = config.backend_api_timeout  ***REMOVED*** Reuse backend timeout
        self._client: Optional[httpx.AsyncClient] = None

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
        headers: Optional[Dict[str, str]] = None,
        form_data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data (JSON)
            headers: Additional headers
            form_data: Form data for OAuth2 requests

        Returns:
            Response data as dictionary

        Raises:
            AuthClientError: If request fails
        """
        client = await self._get_client()

        try:
            if form_data:
                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    data=form_data,
                    headers=headers or {},
                )
            else:
                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=data,
                    headers=headers or {},
                )
            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return cast(Dict[str, Any], response.json())
            else:
                return {"data": response.text}

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {method} {path}: {e}")
            raise AuthClientError(f"Auth service error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {path}: {e}")
            raise AuthClientError(f"Auth service request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {path}: {e}")
            raise AuthClientError(f"Unexpected auth error: {e}")

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Authentication tokens and user info

        Raises:
            AuthClientError: If authentication fails
        """
        return await self._make_request(
            "POST",
            "/auth/tokens",
            form_data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def register(self, email: str, password: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user.

        Args:
            email: User's email address
            password: User's password
            **kwargs: Additional user data (name, etc.)

        Returns:
            New user information

        Raises:
            AuthClientError: If registration fails
        """
        user_data = {"email": email, "password": password, **kwargs}
        return await self._make_request("POST", "/auth/users", data=user_data)

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New authentication tokens

        Raises:
            AuthClientError: If token refresh fails
        """
        return await self._make_request(
            "PUT", "/auth/tokens", data={"refresh_token": refresh_token}
        )

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token.

        Args:
            token: JWT access token

        Returns:
            Token verification result and user info

        Raises:
            AuthClientError: If token verification fails
        """
        return await self._make_request("POST", "/auth/tokens/verify", data={"token": token})

    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user information.

        Args:
            token: JWT access token

        Returns:
            User information

        Raises:
            AuthClientError: If user info retrieval fails
        """
        return await self._make_request(
            "GET", "/auth/users/me", headers={"Authorization": f"Bearer {token}"}
        )
