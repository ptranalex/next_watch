"""Authentication routes for BFF API."""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from bff_api.schemas.auth_schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    AuthenticatedUserResponse,
    TokenVerificationResponse,
)
from bff_api.services.auth_client import AuthClient, AuthClientError
from bff_api.dependencies.common import get_auth_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

***REMOVED*** Security scheme for protected routes
security = HTTPBearer()


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    auth_client: AuthClient = Depends(get_auth_client),
) -> TokenResponse:
    """Authenticate user and return access tokens.

    Args:
        username: User email address
        password: User password
        auth_client: Authentication service client

    Returns:
        JWT access and refresh tokens

    Raises:
        HTTPException: 401 if credentials are invalid, 502 if auth service unavailable
    """
    try:
        response = await auth_client.login(username, password)

        return TokenResponse(
            access_token=response["access_token"],
            refresh_token=response["refresh_token"],
            token_type=response.get("token_type", "bearer"),
            expires_in=response.get("expires_in", 1800),  ***REMOVED*** 30 minutes default
        )

    except AuthClientError as e:
        logger.error(f"Authentication failed for {username}: {e}")
        if "401" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )


@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: RegisterRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> UserResponse:
    """Register a new user account.

    Args:
        user_data: User registration information
        auth_client: Authentication service client

    Returns:
        Created user information

    Raises:
        HTTPException: 400 if user already exists, 502 if auth service unavailable
    """
    try:
        ***REMOVED*** Create name data as a dictionary if present
        name_data = {"full_name": user_data.name} if user_data.name else {}

        response = await auth_client.register(
            email=user_data.email,
            password=user_data.password,
            name=name_data,  ***REMOVED*** Pass as a dictionary
        )

        return UserResponse(
            id=response["id"],
            email=response["email"],
            name=response.get("name"),
            is_active=response.get("is_active", True),
            created_at=response.get("created_at", ""),
        )

    except AuthClientError as e:
        logger.error(f"Registration failed for {user_data.email}: {e}")
        if "400" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> TokenResponse:
    """Refresh access token using refresh token.

    Args:
        token_data: Refresh token request
        auth_client: Authentication service client

    Returns:
        New JWT access and refresh tokens

    Raises:
        HTTPException: 401 if refresh token invalid, 502 if auth service unavailable
    """
    try:
        response = await auth_client.refresh_token(token_data.refresh_token)

        return TokenResponse(
            access_token=response["access_token"],
            refresh_token=response["refresh_token"],
            token_type=response.get("token_type", "bearer"),
            expires_in=response.get("expires_in", 1800),
        )

    except AuthClientError as e:
        logger.error(f"Token refresh failed: {e}")
        if "401" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )


@router.post("/auth/verify", response_model=TokenVerificationResponse)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client),
) -> TokenVerificationResponse:
    """Verify JWT access token and return user information.

    Args:
        credentials: Bearer token from Authorization header
        auth_client: Authentication service client

    Returns:
        Token verification result and user info

    Raises:
        HTTPException: 401 if token invalid, 502 if auth service unavailable
    """
    try:
        response = await auth_client.verify_token(credentials.credentials)

        return TokenVerificationResponse(
            valid=response.get("valid", False),
            user_id=response.get("user_id"),
            email=response.get("email"),
            message=response.get("message"),
        )

    except AuthClientError as e:
        logger.error(f"Token verification failed: {e}")
        if "401" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client),
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        credentials: Bearer token from Authorization header
        auth_client: Authentication service client

    Returns:
        Current user information

    Raises:
        HTTPException: 401 if token invalid, 502 if auth service unavailable
    """
    try:
        ***REMOVED*** Use the new dedicated method to get user info directly
        user_info = await auth_client.get_current_user(credentials.credentials)

        return UserResponse(
            id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name"),
            is_active=user_info.get("is_active", True),
            created_at=user_info.get("created_at", ""),
        )

    except AuthClientError as e:
        logger.error(f"Failed to get user info: {e}")
        if "401" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )


***REMOVED*** Add the new RESTful resource-oriented endpoints that mirror the auth-api
***REMOVED*** These will become the primary endpoints in the future


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: RegisterRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> UserResponse:
    """Create a new user account.

    Args:
        user_data: User registration information
        auth_client: Authentication service client

    Returns:
        Created user information

    Raises:
        HTTPException: 400 if user already exists, 502 if auth service unavailable
    """
    return await register(user_data, auth_client)


@router.get("/users/me", response_model=UserResponse)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client),
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        credentials: Bearer token from Authorization header
        auth_client: Authentication service client

    Returns:
        Current user information

    Raises:
        HTTPException: 401 if token invalid, 502 if auth service unavailable
    """
    return await get_current_user(credentials, auth_client)


@router.post("/tokens", response_model=TokenResponse)
async def create_token(
    username: str = Form(...),
    password: str = Form(...),
    auth_client: AuthClient = Depends(get_auth_client),
) -> TokenResponse:
    """Create authentication tokens.

    Args:
        username: User email address
        password: User password
        auth_client: Authentication service client

    Returns:
        JWT access and refresh tokens

    Raises:
        HTTPException: 401 if credentials are invalid, 502 if auth service unavailable
    """
    return await login(username, password, auth_client)


@router.put("/tokens", response_model=TokenResponse)
async def update_token(
    token_data: RefreshTokenRequest,
    auth_client: AuthClient = Depends(get_auth_client),
) -> TokenResponse:
    """Refresh access token using refresh token.

    Args:
        token_data: Refresh token request
        auth_client: Authentication service client

    Returns:
        New JWT access and refresh tokens

    Raises:
        HTTPException: 401 if refresh token invalid, 502 if auth service unavailable
    """
    return await refresh_access_token(token_data, auth_client)


@router.post("/tokens/verify", response_model=TokenVerificationResponse)
async def verify_token_resource(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client),
) -> TokenVerificationResponse:
    """Verify JWT access token and return user information.

    Args:
        credentials: Bearer token from Authorization header
        auth_client: Authentication service client

    Returns:
        Token verification result and user info

    Raises:
        HTTPException: 401 if token invalid, 502 if auth service unavailable
    """
    return await verify_token(credentials, auth_client)
