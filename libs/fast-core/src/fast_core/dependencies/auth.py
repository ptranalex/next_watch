"""Authentication dependency providers for FastAPI applications.

This module provides authentication-related dependency providers including
API key validation and user authentication.
"""

from typing import Any, Callable, Optional

from config.logging import get_logger
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = get_logger(__name__)

***REMOVED*** Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


def get_api_key() -> Any:
    """Get API key from request headers.

    Returns:
        Dependency function that returns API key string

    Raises:
        HTTPException: If API key is missing or invalid
    """

    def _get_api_key(request: Request) -> str:
        ***REMOVED*** Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  ***REMOVED*** Remove "Bearer " prefix

        ***REMOVED*** Try X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key

        ***REMOVED*** Try query parameter as fallback
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
    verify_user_func: Optional[Callable[[str], Any]] = None,
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
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    ) -> Any:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        ***REMOVED*** If no verification function provided, return the token
        if not verify_user_func:
            return {"token": token}

        try:
            ***REMOVED*** Use provided verification function
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
    required_roles: Optional[list] = None,
    verify_user_func: Optional[Callable[[str], Any]] = None,
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
        ***REMOVED*** If no roles required, just return the user
        if not required_roles:
            return user

        ***REMOVED*** Check if user has required roles
        user_roles = getattr(user, "roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return user

    return Depends(_require_auth)


def get_optional_user(
    verify_user_func: Optional[Callable[[str], Any]] = None,
) -> Any:
    """Get current user if authenticated, None otherwise.

    Args:
        verify_user_func: Optional function to verify and load user

    Returns:
        Dependency function that returns current user object or None
    """

    def _get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    ) -> Optional[Any]:
        if not credentials:
            return None

        try:
            token = credentials.credentials

            ***REMOVED*** If no verification function provided, return the token
            if not verify_user_func:
                return {"token": token}

            ***REMOVED*** Use provided verification function
            user = verify_user_func(token)
            return user
        except Exception as e:
            logger.debug(f"Optional authentication failed: {e}")
            return None

    return Depends(_get_optional_user)
