"""Authentication dependencies for Auth API routes."""

from typing import Annotated

from config.logging import get_logger

***REMOVED*** Import enhanced error handling
from fast_core.errors import (
    critical_service_handler,
)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from auth_api.db.database import get_db
from auth_api.models.user import User
from auth_api.services.auth_service import AuthService

logger = get_logger(__name__)

***REMOVED*** OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/tokens")


def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    return AuthService()


@critical_service_handler("auth-service", logger)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Get the current authenticated user from the token.

    This is a CRITICAL operation used by protected endpoints.

    Args:
        token: JWT access token
        session: Database session
        auth_service: Authentication service

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails (maintains FastAPI compatibility)
        ExternalServiceException: If database is unavailable (critical failure)
    """
    user = auth_service.get_user_by_token(session, token)
    if not user:
        ***REMOVED*** Convert to HTTPException for FastAPI compatibility
        ***REMOVED*** The enhanced error handling preserves semantic information in logs
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
