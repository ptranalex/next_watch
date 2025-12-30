"""Authentication dependency providers for FastAPI applications.

This module provides authentication-related dependency providers including
API key validation and user authentication.
"""

from collections.abc import Callable
from typing import Any

from config.logging import get_logger
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = get_logger(__name__)

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


def get_api_key() -> Any:
    """Get API key from request headers.

    Returns:
        Dependency function that returns API key string

    Raises:
        HTTPException: If API key is missing or invalid
    """

    def _get_api_key(request: Request) -> str:
        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        # Try X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key

        # Try query parameter as fallback
        api_key = request.query_params.get("api_key")
        if api_key:
            return api_key

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Depends(_get_api_key)


def get_current_user(
    verify_user_func: Callable[[str], Any] | None = None,
) -> Any:
    """Get current authenticated user.

    Args:
        verify_user_func: Optional function to verify and load user

    Returns:
        Dependency function that returns current user object

    Raises:
        HTTPException: If authentication fails
    """

    def _get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> Any:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        # If no verification function provided, return the token
        if not verify_user_func:
            return {"token": token}

        try:
            # Use provided verification function
            user = verify_user_func(token)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return Depends(_get_current_user)


def require_auth(
    required_roles: list | None = None,
    verify_user_func: Callable[[str], Any] | None = None,
) -> Any:
    """Require authentication with optional role checking.

    Args:
        required_roles: List of required roles
        verify_user_func: Function to verify and load user

    Returns:
        Dependency function that returns current user object

    Raises:
        HTTPException: If authentication or authorization fails
    """

    def _require_auth(
        user: Any = Depends(get_current_user(verify_user_func)),
    ) -> Any:
        # If no roles required, just return the user
        if not required_roles:
            return user

        # Check if user has required roles
        user_roles = getattr(user, "roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return user

    return Depends(_require_auth)


def get_optional_user(
    verify_user_func: Callable[[str], Any] | None = None,
) -> Any:
    """Get current user if authenticated, None otherwise.

    Args:
        verify_user_func: Optional function to verify and load user

    Returns:
        Dependency function that returns current user object or None
    """

    def _get_optional_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> Any | None:
        if not credentials:
            return None

        try:
            token = credentials.credentials

            # If no verification function provided, return the token
            if not verify_user_func:
                return {"token": token}

            # Use provided verification function
            user = verify_user_func(token)
            return user
        except Exception as e:
            logger.debug(f"Optional authentication failed: {e}")
            return None

    return Depends(_get_optional_user)
