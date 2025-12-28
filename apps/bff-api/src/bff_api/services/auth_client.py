"""Authentication client for communicating with auth service."""

from typing import Any, cast

import httpx
from config.logging import get_logger
from fast_core.dependencies.client_factory import ServiceClientConfig
from fast_core.errors import service_error_handler
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

***REMOVED*** Import BaseBackendClient for inheritance instead of BaseServiceClient
from bff_api.services.clients.base import (
    BackendClientError,
    BackendClientPermanentError,
    BackendClientTransientError,
    BaseBackendClient,
)

logger = get_logger(__name__)


***REMOVED*** Use BackendClient error classes instead of duplicating
class AuthClientError(BackendClientError):
    """Base exception for auth client errors - inherits from BackendClientError."""

    pass


class AuthClientTransientError(BackendClientTransientError):
    """Transient error that can be retried (network issues, 5xx errors)."""

    pass


class AuthClientPermanentError(BackendClientPermanentError):
    """Permanent error that should not be retried (4xx errors)."""

    pass


class AuthClient(BaseBackendClient):
    """HTTP client for communicating with authentication service.

    Now inherits from BaseBackendClient for consistent error handling,
    retry logic, and header propagation across all BFF clients.
    """

    def __init__(self, config: ServiceClientConfig) -> None:
        """Initialize auth client.

        Args:
            config: Service client configuration
        """
        super().__init__(config)
        ***REMOVED*** Override service name for proper error attribution
        self.service_name = "auth-api"

    def _build_api_path(self, path: str) -> str:
        """Build API path for auth service endpoints.

        Auth API uses /auth/v1/ prefix instead of /api/v1/ used by backend API.

        Args:
            path: Relative API path (e.g., "/tokens", "/users")

        Returns:
            Full API path with auth service prefix (e.g., "/auth/v1/tokens")
        """
        ***REMOVED*** Remove leading slash if present to avoid double slashes
        clean_path = path.lstrip("/")
        return f"/auth/v1/{clean_path}"

    @service_error_handler("auth-api", logger)
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
        headers: dict[str, str] | None = None,
        form_data: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with auth-specific handling.

        This method is needed because:
        1. @service_error_handler uses hardcoded "auth-api" service name
        2. Supports form_data parameter for OAuth2 requests
        3. Delegates to parent for all standard HTTP logic
        """
        if form_data:
            ***REMOVED*** Handle OAuth2 form data requests
            client = await self._get_client()
            request_headers = self._get_request_headers(headers)

            try:
                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    data=form_data,
                    headers=request_headers,
                )
                response.raise_for_status()

                if response.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    return cast(dict[str, Any], response.json())
                else:
                    return {"data": response.text}

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if 400 <= status_code < 500:
                    if status_code == 401:
                        logger.debug(
                            f"Authentication failed for {method} {path}: {status_code}"
                        )
                    elif status_code == 404:
                        logger.debug(
                            f"Resource not found for {method} {path}: {status_code}"
                        )
                    else:
                        logger.info(f"Client error {status_code} for {method} {path}")
                    raise AuthClientPermanentError(f"Auth service error: {status_code}")
                else:
                    logger.error(f"Server error {status_code} for {method} {path}: {e}")
                    raise AuthClientTransientError(f"Auth service error: {status_code}")

            except httpx.RequestError as e:
                logger.error(f"Request error for {method} {path}: {e}")
                raise AuthClientTransientError(f"Auth service request failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {method} {path}: {e}")
                raise AuthClientPermanentError(f"Unexpected auth error: {e}")
        else:
            ***REMOVED*** Delegate standard JSON requests to parent implementation
            return await super()._make_request(method, path, params, data, headers)

    async def login(self, email: str, password: str) -> dict[str, Any]:
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
            self._build_api_path("/tokens"),
            form_data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def register(
        self, email: str, password: str, username: str | None = None
    ) -> dict[str, Any]:
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

        return await self._make_request(
            "POST", self._build_api_path("/users"), data=user_data
        )

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New authentication tokens

        Raises:
            AuthClientError: If token refresh fails
        """
        return await self._make_request(
            "PUT",
            self._build_api_path("/tokens"),
            data={"refresh_token": refresh_token},
        )

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode JWT token.

        Args:
            token: JWT access token

        Returns:
            Token verification result and user info

        Raises:
            AuthClientError: If token verification fails
        """
        return await self._make_request(
            "POST", self._build_api_path("/tokens/verify"), data={"token": token}
        )

    async def get_current_user(self, token: str) -> dict[str, Any]:
        """Get current user information.

        Args:
            token: JWT access token

        Returns:
            User information

        Raises:
            AuthClientError: If user info retrieval fails
        """
        return await self._make_request(
            "GET",
            self._build_api_path("/users/me"),
            headers={"Authorization": f"Bearer {token}"},
        )
