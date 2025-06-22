"""Authentication dependencies for BFF API routes."""

from typing import Optional, Tuple

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fast_core.errors.exceptions import AuthenticationException

from config.logging import get_logger
from bff_api.utils.auth import extract_user_id_from_token

logger = get_logger(__name__)

***REMOVED*** Security scheme
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Get current authenticated user ID from JWT token.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User ID

    Raises:
        AuthenticationException: If token is invalid or missing
    """
    if not credentials or not credentials.credentials:
        logger.error("Authentication required", service="bff", endpoint="get_current_user_id")
        raise AuthenticationException(
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = extract_user_id_from_token(credentials.credentials)
    if user_id is None:
        raise AuthenticationException(
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_current_user_id_and_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Tuple[int, str]:
    """Get current authenticated user ID and JWT token.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        Tuple of (user_id, jwt_token)

    Raises:
        AuthenticationException: If token is invalid or missing
    """
    if not credentials or not credentials.credentials:
        logger.error(
            "Authentication required", service="bff", endpoint="get_current_user_id_and_token"
        )
        raise AuthenticationException(
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = extract_user_id_from_token(credentials.credentials)
    if user_id is None:
        logger.error(
            "Invalid or expired token", service="bff", endpoint="get_current_user_id_and_token"
        )
        raise AuthenticationException(
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id, credentials.credentials


def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[int]:
    """Get optional user ID from JWT token.

    Args:
        credentials: Optional Bearer token from Authorization header

    Returns:
        User ID if authenticated, None otherwise
    """
    if not credentials or not credentials.credentials:
        return None

    return extract_user_id_from_token(credentials.credentials)
