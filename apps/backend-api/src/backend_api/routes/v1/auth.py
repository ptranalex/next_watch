"""
Authentication routes for user registration, login, and token management.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from movie_storage.models.user import User
from sqlmodel import Session

from backend_api.db import get_db
from backend_api.schemas import (
    RefreshToken,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from backend_api.services.auth import AuthService

***REMOVED*** Create router
router = APIRouter(prefix="/auth", tags=["auth"])

***REMOVED*** OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


***REMOVED*** Authentication dependencies
def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    return AuthService()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Get the current authenticated user from the token.

    Args:
        token: JWT access token
        session: Database session
        auth_service: Authentication service

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails
    """
    user = auth_service.get_user_by_token(session, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_optional_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Optional[User]:
    """
    Get the current user if authenticated, or None if not.

    Args:
        token: JWT access token (optional)
        session: Database session
        auth_service: Authentication service

    Returns:
        User object if authenticated, None otherwise
    """
    if not token:
        return None

    return auth_service.get_user_by_token(session, token)


***REMOVED*** Authentication endpoints
@router.post("/signup/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Register a new user.

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


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Authenticate a user and return access and refresh tokens.

    Args:
        form_data: OAuth2 form with username (email) and password
        session: Database session
        auth_service: Authentication service

    Returns:
        Token response with access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    ***REMOVED*** OAuth2PasswordRequestForm uses 'username' field, but we expect email
    user = auth_service.authenticate(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    ***REMOVED*** We've already checked that user is not None, and we know it has an ID
    assert user.id is not None, "User ID is unexpectedly None"

    ***REMOVED*** Generate tokens
    tokens = auth_service.generate_tokens(user.id)
    return Token(**tokens)


@router.post("/login/json", response_model=Token)
async def login_json(
    login_data: UserLogin,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Authenticate a user with JSON payload and return tokens.

    This endpoint provides an alternative to the form-based login
    for clients that prefer to send JSON.

    Args:
        login_data: User login data
        session: Database session
        auth_service: Authentication service

    Returns:
        Token response with access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    user = auth_service.authenticate(session, login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    ***REMOVED*** We've already checked that user is not None, and we know it has an ID
    assert user.id is not None, "User ID is unexpectedly None"

    ***REMOVED*** Generate tokens
    tokens = auth_service.generate_tokens(user.id)
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Refresh the access token using a refresh token.

    Args:
        refresh_data: Refresh token data
        auth_service: Authentication service

    Returns:
        New token pair

    Raises:
        HTTPException: If refresh token is invalid
    """
    new_tokens = auth_service.refresh_tokens(refresh_data.refresh_token)

    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(**new_tokens)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Get information about the currently authenticated user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return current_user
