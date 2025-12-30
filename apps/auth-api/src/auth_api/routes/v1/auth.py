"""
Authentication routes for Auth API v1.

Handles token operations: login, refresh, and verification.
"""

from typing import Annotated

from config.logging import get_logger

# Import enhanced error handling
from fast_core.errors import (
    AuthenticationException,
    ValidationException,
    critical_service_handler,
    service_error_handler,
)
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from auth_api.core.metrics import (
    get_auth_metrics,
    track_authentication,
    track_token_operation,
)
from auth_api.dependencies import get_auth_service, get_db
from auth_api.schemas.auth_schemas import (
    RefreshToken,
    Token,
    TokenVerificationRequest,
    TokenVerificationResponse,
)
from auth_api.services.auth_service import AuthService

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/tokens", response_model=Token)
@track_authentication
@service_error_handler(
    service_name="auth-database",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "invalid_credentials": lambda e: AuthenticationException("Invalid email or password"),
        "user_not_found": lambda e: AuthenticationException("User account not found"),
        "account_locked": lambda e: AuthenticationException("Account temporarily locked"),
        "account_disabled": lambda e: AuthenticationException("Account is disabled"),
    },
)
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
        AuthenticationException: If authentication fails (preserves semantic meaning)
        ValidationException: If input validation fails
    """
    # Record authentication attempt metrics
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_auth_request("login", "attempt", 0.0)  # Duration tracked by decorator
        metrics.record_api_client_request("bff", "/tokens", "attempt")
        metrics.record_database_operation("select", "users", "attempt", 0.0)

    # Validate input
    if not form_data.username or not form_data.username.strip():
        raise ValidationException("Email is required")
    if not form_data.password or not form_data.password.strip():
        raise ValidationException("Password is required")

    # OAuth2PasswordRequestForm uses 'username' field, but we expect email
    user = auth_service.authenticate(session, form_data.username.strip(), form_data.password)

    if not user:
        # Record authentication failure
        if metrics:
            metrics.record_auth_failure("invalid_credentials", "login")
            metrics.record_auth_request("login", "failure", 0.0)
            metrics.record_api_client_request("bff", "/tokens", "failure")
            metrics.record_security_event("login_failure", "medium")
            metrics.record_brute_force_attempt("ip", blocked=False)
            metrics.record_suspicious_activity("failed_login", "medium")
            metrics.record_database_operation("select", "users", "failure", 0.0)

        # Raise semantic exception instead of generic HTTPException
        raise AuthenticationException("Invalid email or password")

    # We've already checked that user is not None, and we know it has an ID
    assert user.id is not None, "User ID is unexpectedly None"

    # Generate tokens
    tokens = auth_service.generate_tokens(user.id)

    # Record successful authentication
    if metrics:
        metrics.record_auth_request("login", "success", 0.0)
        metrics.record_api_client_request("bff", "/tokens", "success")
        metrics.record_jwt_operation("create", "access", "success", 0.0)
        metrics.record_jwt_operation("create", "refresh", "success", 0.0)
        metrics.record_user_operation("authenticate", "success")
        metrics.record_database_operation("select", "users", "success", 0.0)
        metrics.record_session_operation("create", "success")
        metrics.record_password_operation("verify", "success")
        # Update active tokens and users (simplified - in real app would query actual counts)
        metrics.update_active_tokens("access", 1)
        metrics.update_active_tokens("refresh", 1)
        metrics.update_active_users(1)
        # Record response size (simplified - in real app would calculate actual size)
        metrics.record_response_size("login", 500)  # Approximate token response size
        metrics.record_cache_performance("user", "miss")  # User lookup cache
        # Update database connection pool and concurrent sessions (simplified)
        metrics.update_database_connection_pool(5)  # Example active connections
        metrics.update_concurrent_sessions(10)  # Example concurrent sessions

    return Token(**tokens)


@router.put("/tokens", response_model=Token)
@track_token_operation
@service_error_handler(
    service_name="auth-database",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "invalid_token": lambda e: AuthenticationException("Invalid refresh token"),
        "expired_token": lambda e: AuthenticationException("Refresh token has expired"),
        "token_revoked": lambda e: AuthenticationException("Refresh token has been revoked"),
    },
)
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
        AuthenticationException: If refresh token is invalid (preserves semantic meaning)
        ValidationException: If input validation fails
    """
    # Record token refresh attempt
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_auth_request("refresh", "attempt", 0.0)
        metrics.record_api_client_request("bff", "/tokens", "attempt")
        metrics.record_database_operation("select", "tokens", "attempt", 0.0)

    # Validate input
    if not refresh_data.refresh_token or not refresh_data.refresh_token.strip():
        raise ValidationException("Refresh token is required")

    new_tokens = auth_service.refresh_tokens(refresh_data.refresh_token.strip())

    if not new_tokens:
        # Record refresh failure
        if metrics:
            metrics.record_auth_failure("invalid_refresh_token", "refresh")
            metrics.record_auth_request("refresh", "failure", 0.0)
            metrics.record_jwt_validation("invalid", "expired_or_invalid")
            metrics.record_api_client_request("bff", "/tokens", "failure")
            metrics.record_security_event("token_misuse", "medium")
            metrics.record_suspicious_activity("invalid_refresh", "medium")
            metrics.record_database_operation("select", "tokens", "failure", 0.0)

        # Raise semantic exception instead of generic HTTPException
        raise AuthenticationException("Invalid refresh token")

    # Record successful token refresh
    if metrics:
        metrics.record_auth_request("refresh", "success", 0.0)
        metrics.record_jwt_operation("refresh", "access", "success", 0.0)
        metrics.record_jwt_operation("create", "refresh", "success", 0.0)
        metrics.record_api_client_request("bff", "/tokens", "success")
        metrics.record_token_refresh_pattern("manual", "expired")
        metrics.record_database_operation("select", "tokens", "success", 0.0)
        metrics.record_database_operation("update", "tokens", "success", 0.0)
        # Update active tokens
        metrics.update_active_tokens("access", 1)
        metrics.update_active_tokens("refresh", 1)
        # Record response size and cache performance
        metrics.record_response_size("refresh", 500)  # Approximate token response size
        metrics.record_cache_performance("token", "hit")  # Token validation cache
        # Update database connection pool
        metrics.update_database_connection_pool(3)  # Example active connections

    return Token(**new_tokens)


@router.post("/tokens/verify", response_model=TokenVerificationResponse)
@track_token_operation
@critical_service_handler("auth-database", logger)
async def verify_token(
    request: TokenVerificationRequest,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenVerificationResponse:
    """
    Verify a JWT token and return user information.

    Used by BFF: POST /auth/v1/tokens/verify

    This endpoint is used by the BFF service to validate tokens from the frontend.
    This is a CRITICAL operation that must always work for the platform to function.

    Args:
        request: Token verification request containing the JWT token
        session: Database session
        auth_service: Authentication service

    Returns:
        Token verification response with user info or error details

    Raises:
        ValidationException: If input validation fails
        ExternalServiceException: If database is unavailable (critical failure)
    """
    # Record token verification attempt
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_auth_request("verify", "attempt", 0.0)
        metrics.record_api_client_request("bff", "/tokens/verify", "attempt")
        metrics.record_database_operation("select", "users", "attempt", 0.0)

    # Validate input
    if not request.token or not request.token.strip():
        raise ValidationException("Token is required")

    # Verify the token - this always returns a result, never raises
    result = auth_service.verify_token(session, request.token.strip())

    # Record verification result metrics
    if metrics:
        if result.valid:
            metrics.record_auth_request("verify", "success", 0.0)
            metrics.record_jwt_validation("valid", "none")
            metrics.record_api_client_request("bff", "/tokens/verify", "success")
            metrics.record_database_operation("select", "users", "success", 0.0)
            metrics.record_session_operation("validate", "success")
            metrics.record_response_size("verify", 200)  # Approximate user info response size
            metrics.record_cache_performance("user", "hit")  # User lookup cache
        else:
            metrics.record_auth_request("verify", "failure", 0.0)
            metrics.record_jwt_validation("invalid", result.error or "unknown")
            metrics.record_api_client_request("bff", "/tokens/verify", "failure")
            metrics.record_security_event("token_verification_failed", "medium")
            metrics.record_suspicious_activity("invalid_token", "medium")
            metrics.record_database_operation("select", "users", "failure", 0.0)
            metrics.record_response_size("verify", 100)  # Error response size
            metrics.record_cache_performance("user", "miss")  # User lookup cache

    return result
