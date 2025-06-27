"""
Authentication routes for Auth API v1.

Handles token operations: login, refresh, and verification.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from auth_api.schemas.auth_schemas import (
    Token,
    RefreshToken,
    TokenVerificationRequest,
    TokenVerificationResponse,
)
from auth_api.dependencies import get_auth_service, get_db
from auth_api.services.auth_service import AuthService
from auth_api.core.metrics import (
    get_auth_metrics,
    track_authentication,
    track_token_operation,
)

***REMOVED*** Create router
router = APIRouter()


@router.post("/tokens", response_model=Token)
@track_authentication
async def create_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Authenticate a user and return access and refresh tokens.

    Used by BFF: POST /auth/v1/tokens (form data)

    Args:
        form_data: OAuth2 form with username (email) and password
        session: Database session
        auth_service: Authentication service

    Returns:
        Token response with access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    ***REMOVED*** Record authentication attempt metrics
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_auth_request("login", "attempt", 0.0)  ***REMOVED*** Duration tracked by decorator
        metrics.record_api_client_request("bff", "/tokens", "attempt")

    ***REMOVED*** OAuth2PasswordRequestForm uses 'username' field, but we expect email
    user = auth_service.authenticate(session, form_data.username, form_data.password)

    if not user:
        ***REMOVED*** Record authentication failure
        if metrics:
            metrics.record_auth_failure("invalid_credentials", "login")
            metrics.record_auth_request("login", "failure", 0.0)
            metrics.record_api_client_request("bff", "/tokens", "failure")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    ***REMOVED*** We've already checked that user is not None, and we know it has an ID
    assert user.id is not None, "User ID is unexpectedly None"

    ***REMOVED*** Generate tokens
    tokens = auth_service.generate_tokens(user.id)

    ***REMOVED*** Record successful authentication
    if metrics:
        metrics.record_auth_request("login", "success", 0.0)
        metrics.record_api_client_request("bff", "/tokens", "success")
        metrics.record_jwt_operation("create", "access", "success", 0.0)
        metrics.record_jwt_operation("create", "refresh", "success", 0.0)
        metrics.record_user_operation("authenticate", "success")

    return Token(**tokens)


@router.put("/tokens", response_model=Token)
@track_token_operation
async def refresh_token(
    refresh_data: RefreshToken,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Refresh the access token using a refresh token.

    Used by BFF: PUT /auth/v1/tokens

    Args:
        refresh_data: Refresh token data
        auth_service: Authentication service

    Returns:
        New token pair

    Raises:
        HTTPException: If refresh token is invalid
    """
    ***REMOVED*** Record token refresh attempt
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_auth_request("refresh", "attempt", 0.0)
        metrics.record_api_client_request("bff", "/tokens", "attempt")

    new_tokens = auth_service.refresh_tokens(refresh_data.refresh_token)

    if not new_tokens:
        ***REMOVED*** Record refresh failure
        if metrics:
            metrics.record_auth_failure("invalid_refresh_token", "refresh")
            metrics.record_auth_request("refresh", "failure", 0.0)
            metrics.record_jwt_validation("invalid", "expired_or_invalid")
            metrics.record_api_client_request("bff", "/tokens", "failure")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    ***REMOVED*** Record successful token refresh
    if metrics:
        metrics.record_auth_request("refresh", "success", 0.0)
        metrics.record_jwt_operation("refresh", "access", "success", 0.0)
        metrics.record_jwt_operation("create", "refresh", "success", 0.0)
        metrics.record_api_client_request("bff", "/tokens", "success")
        metrics.record_token_refresh_pattern("manual", "expired")

    return Token(**new_tokens)


@router.post("/tokens/verify", response_model=TokenVerificationResponse)
@track_token_operation
async def verify_token(
    request: TokenVerificationRequest,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenVerificationResponse:
    """
    Verify a JWT token and return user information.

    Used by BFF: POST /auth/v1/tokens/verify

    This endpoint is used by the BFF service to validate tokens from the frontend.

    Args:
        request: Token verification request containing the JWT token
        session: Database session
        auth_service: Authentication service

    Returns:
        Token verification response with user info or error details
    """
    ***REMOVED*** Record token verification attempt
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_auth_request("verify", "attempt", 0.0)
        metrics.record_api_client_request("bff", "/tokens/verify", "attempt")

    ***REMOVED*** Verify the token
    result = auth_service.verify_token(session, request.token)

    ***REMOVED*** Record verification result metrics
    if metrics:
        if result.valid:
            metrics.record_auth_request("verify", "success", 0.0)
            metrics.record_jwt_validation("valid", "none")
            metrics.record_api_client_request("bff", "/tokens/verify", "success")
        else:
            metrics.record_auth_request("verify", "failure", 0.0)
            metrics.record_jwt_validation("invalid", result.error or "unknown")
            metrics.record_api_client_request("bff", "/tokens/verify", "failure")

    return result
