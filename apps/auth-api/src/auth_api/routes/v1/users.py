"""
User management routes for Auth API v1.

Handles user registration and profile operations.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from auth_api.schemas.auth_schemas import (
    UserCreate,
    UserResponse,
)
from auth_api.dependencies import get_auth_service, get_current_user, get_db
from auth_api.models.user import User
from auth_api.services.auth_service import AuthService

***REMOVED*** Create router
router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Register a new user.

    Used by BFF: POST /auth/v1/users

    Args:
        user_data: User registration data
        session: Database session
        auth_service: Authentication service

    Returns:
        Newly created user

    Raises:
        HTTPException: If registration fails
    """
    try:
        user = auth_service.register_user(
            session,
            user_data.email,
            user_data.password,
            user_data.username,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get information about the currently authenticated user.

    Used by BFF: GET /auth/v1/users/me

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return current_user
