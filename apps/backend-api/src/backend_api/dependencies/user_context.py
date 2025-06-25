"""
User context dependencies for backend API.

In the new architecture, the BFF validates user tokens and authenticates to Backend API
using an internal service token, then passes the verified user_id via headers.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend_api.config import settings

security = HTTPBearer()


async def verify_internal_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> bool:
    """
    Verify the internal service token from BFF.

    Args:
        credentials: Bearer token credentials

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is invalid
    """
    if not credentials or credentials.credentials != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal service token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


async def get_user_id_from_header(
    x_user_id: Annotated[Optional[str], Header(alias="X-User-ID")] = None,
    _: bool = Depends(verify_internal_token),
) -> int:
    """
    Extract user ID from X-User-ID header injected by authenticated BFF.

    Args:
        x_user_id: User ID from X-User-ID header
        _: Internal token verification (dependency)

    Returns:
        User ID as integer

    Raises:
        HTTPException: If X-User-ID header is missing or invalid
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-ID header is required",
        )

    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-ID format",
        )


async def get_optional_user_id_from_header(
    x_user_id: Annotated[Optional[str], Header(alias="X-User-ID")] = None,
) -> Optional[int]:
    """
    Extract optional user ID from X-User-ID header injected by BFF.

    Args:
        x_user_id: User ID from X-User-ID header

    Returns:
        User ID as integer, or None if header not present
    """
    if not x_user_id:
        return None

    try:
        return int(x_user_id)
    except ValueError:
        return None
