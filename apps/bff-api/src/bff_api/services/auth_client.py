"""Authentication client for communicating with auth service."""

import logging
from typing import Any, Dict, Optional, TypeVar, cast

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from bff_api.config.app import BFFAPIConfig
from config.logging import get_logger
from fast_core.dependencies.client_factory import BaseServiceClient, ServiceClientConfig

logger = get_logger(__name__)


class AuthClientError(Exception):
    """Base exception for auth client errors."""

    pass


class AuthClientTransientError(AuthClientError):
    """Transient error that can be retried (network issues, 5xx errors)."""

    pass


class AuthClientPermanentError(AuthClientError):
    """Permanent error that should not be retried (4xx errors)."""

    pass


class AuthClient(BaseServiceClient):
    """HTTP client for communicating with authentication service."""

    def __init__(self, config: ServiceClientConfig) -> None:
        """Initialize auth client.

        Args:
            config: Service client configuration
        """
        super().__init__(config)

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the auth service."""
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return {
                "service": self.name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "url": str(client.base_url),
            }
        except Exception as e:
            logger.warning(f"Health check failed for {self.name}: {e}")
            return {
                "service": self.name,
                "status": "error",
                "error": str(e),
                "url": self.base_url,
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(AuthClientTransientError),
    )
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
            status_code = e.response.status_code

            ***REMOVED*** 4xx errors are permanent (don't retry)
            if 400 <= status_code < 500:
                ***REMOVED*** Log 4xx as debug/info - these are often expected (auth failures, bad requests)
                if status_code == 401:
                    logger.debug(f"Authentication failed for {method} {path}: {status_code}")
                elif status_code == 404:
                    logger.debug(f"Resource not found for {method} {path}: {status_code}")
                else:
                    logger.info(f"Client error {status_code} for {method} {path}")
                raise AuthClientPermanentError(f"Auth service error: {status_code}")
            ***REMOVED*** 5xx errors are transient (can retry) - these are actual system errors
            else:
                logger.error(f"Server error {status_code} for {method} {path}: {e}")
                raise AuthClientTransientError(f"Auth service error: {status_code}")

        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {path}: {e}")
            ***REMOVED*** Network errors are transient (can retry)
            raise AuthClientTransientError(f"Auth service request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {path}: {e}")
            ***REMOVED*** Unexpected errors are treated as permanent
            raise AuthClientPermanentError(f"Unexpected auth error: {e}")

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
            "/auth/v1/tokens",
            form_data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def register(
        self, email: str, password: str, username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new user.

        Args:
            email: User's email address
            password: User's password
            username: Optional username

        Returns:
            New user information

        Raises:
            AuthClientError: If registration fails
        """
        user_data = {
            "email": email,
            "password": password,
            "password_confirm": password,  ***REMOVED*** Auth-api requires password confirmation
        }
        if username:
            user_data["username"] = username

        return await self._make_request("POST", "/auth/v1/users", data=user_data)

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
            "PUT", "/auth/v1/tokens", data={"refresh_token": refresh_token}
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
        return await self._make_request("POST", "/auth/v1/tokens/verify", data={"token": token})

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
            "GET", "/auth/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
