"""Authentication routes for BFF API."""

from typing import Any, Dict

from config.logging import get_logger
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_api.dependencies import get_auth_client
from bff_api.schemas.auth_schemas import (
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    TokenVerificationResponse,
    UserResponse,
)
from bff_api.services.auth_client import (
    AuthClient,
    AuthClientError,
    AuthClientPermanentError,
    AuthClientTransientError,
)

logger = get_logger(__name__)
router = APIRouter(tags=["authentication"])

***REMOVED*** Security scheme for protected routes
security = HTTPBearer()


***REMOVED*** ============================================================================
***REMOVED*** Resource-Oriented Authentication Endpoints
***REMOVED*** ============================================================================


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
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
        response = await auth_client.register(
            email=user_data.email,
            password=user_data.password,
            username=user_data.name,  ***REMOVED*** Map name to username for auth-api
        )

        return UserResponse(
            id=response["id"],
            email=response["email"],
            name=response.get("username"),  ***REMOVED*** Map back from username
            is_active=response.get("is_active", True),
            created_at=response.get("created_at", ""),
        )

    except AuthClientError as e:
        logger.error(
            "Registration failed",
            email=user_data.email,
            error=str(e),
            service="bff",
            endpoint="create_user",
        )
        if "400" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )


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
    try:
        user_info = await auth_client.get_current_user(credentials.credentials)

        return UserResponse(
            id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("username"),  ***REMOVED*** Map from auth-api username
            is_active=user_info.get("is_active", True),
            created_at=user_info.get("created_at", ""),
        )

    except AuthClientError as e:
        if "401" in str(e):
            ***REMOVED*** Token validation failures are normal - log as info
            logger.info("Token validation failed", service="bff", endpoint="get_user_profile")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            ***REMOVED*** Service errors are actual problems - log as error
            logger.error(
                "User profile service error",
                error=str(e),
                service="bff",
                endpoint="get_user_profile",
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication service unavailable",
            )


@router.post("/tokens", response_model=TokenResponse)
async def create_token(
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
        if "401" in str(e):
            ***REMOVED*** Authentication failures are normal user behavior - log as info
            logger.info(
                "Authentication attempt failed",
                username=username,
                service="bff",
                endpoint="create_token",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            ***REMOVED*** Service errors are actual problems - log as error
            logger.error(
                "Authentication service error",
                username=username,
                error=str(e),
                service="bff",
                endpoint="create_token",
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication service unavailable",
            )


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
    try:
        response = await auth_client.refresh_token(token_data.refresh_token)

        return TokenResponse(
            access_token=response["access_token"],
            refresh_token=response["refresh_token"],
            token_type=response.get("token_type", "bearer"),
            expires_in=response.get("expires_in", 1800),
        )

    except AuthClientError as e:
        if "401" in str(e):
            ***REMOVED*** Token refresh failures are normal - log as info
            logger.info("Token refresh failed", service="bff", endpoint="update_token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            ***REMOVED*** Service errors are actual problems - log as error
            logger.error(
                "Token refresh service error", error=str(e), service="bff", endpoint="update_token"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication service unavailable",
            )


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
    try:
        response = await auth_client.verify_token(credentials.credentials)

        return TokenVerificationResponse(
            valid=response.get("valid", False),
            user_id=response.get("user_id"),
            email=response.get("email"),
            message=response.get("error") if not response.get("valid") else None,
        )

    except AuthClientError as e:
        logger.error(
            "Token verification failed",
            error=str(e),
            service="bff",
            endpoint="verify_token_resource",
        )
        return TokenVerificationResponse(
            valid=False, message="Token verification service unavailable"
        )
