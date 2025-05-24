"""
Authentication routes for dedicated auth service.

Handles user authentication, registration, token management, and token verification for BFF.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from auth_api.schemas.auth_schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    RefreshToken,
    TokenVerificationRequest,
    TokenVerificationResponse,
)
from auth_api.services.auth_service import AuthService
from auth_api.db.database import get_db
from movie_storage.models.user import User

***REMOVED*** Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

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


***REMOVED*** ============================================================================
***REMOVED*** NEW: Token Verification Endpoint for BFF
***REMOVED*** ============================================================================


@router.post("/verify-token", response_model=TokenVerificationResponse)
async def verify_token(
    request: TokenVerificationRequest,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenVerificationResponse:
    """
    Verify a JWT token and return user information.

    This endpoint is used by the BFF service to validate tokens from the frontend.

    Args:
        request: Token verification request containing the JWT token
        session: Database session
        auth_service: Authentication service

    Returns:
        Token verification response with user info or error details
    """
    return auth_service.verify_token(session, request.token)


***REMOVED*** ============================================================================
***REMOVED*** Authentication Endpoints
***REMOVED*** ============================================================================


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
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
    Authenticate a user with form data and return access and refresh tokens.

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
