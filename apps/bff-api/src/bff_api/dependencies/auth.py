"""Authentication dependencies for BFF API routes."""

import logging
from typing import Optional, Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from bff_api.utils.auth import extract_user_id_from_token

logger = logging.getLogger(__name__)

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
        HTTPException: 401 if token is invalid or missing
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = extract_user_id_from_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
        HTTPException: 401 if token is invalid or missing
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = extract_user_id_from_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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