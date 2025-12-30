"""
User management routes for Auth API v1.

Handles user registration and profile operations.
"""

from typing import Annotated

from config.logging import get_logger

# Import enhanced error handling
from fast_core.errors import (
    ConflictException,
    ValidationException,
    critical_service_handler,
    service_error_handler,
)
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from auth_api.core.metrics import (
    get_auth_metrics,
    track_user_management,
    track_user_registration,
)
from auth_api.dependencies import get_auth_service, get_current_user, get_db
from auth_api.models.user import User
from auth_api.schemas.auth_schemas import UserCreate, UserResponse
from auth_api.services.auth_service import AuthService

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@track_user_registration
@service_error_handler(
    service_name="auth-database",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "email already exists": lambda e: ConflictException(
            detail="A user with this email address already exists",
            conflicting_resource={
                "type": "User",
                "email": str(e).split()[-1] if str(e).split() else "unknown",
            },
        ),
        "username already exists": lambda e: ConflictException(
            detail="A user with this username already exists",
            conflicting_resource={
                "type": "User",
                "username": str(e).split()[-1] if str(e).split() else "unknown",
            },
        ),
    },
)
async def create_user(
    user_data: UserCreate,
    session: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Register a new user account.

    Used by BFF: POST /bff/v1/users

    Args:
        user_data: User registration data
        session: Database session
        auth_service: Authentication service

    Returns:
        Created user object

    Raises:
        ConflictException: If email or username already exists (preserves semantic meaning)
        ValidationException: If input validation fails
    """
    # Record registration attempt
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_user_operation("register", "attempt")
        metrics.record_api_client_request("bff", "/users", "attempt")
        metrics.record_database_operation("insert", "users", "attempt", 0.0)

    # Validate input data
    if not user_data.email or not user_data.email.strip():
        raise ValidationException("Email is required")
    if not user_data.password or not user_data.password.strip():
        raise ValidationException("Password is required")
    if len(user_data.password) < 8:
        raise ValidationException("Password must be at least 8 characters long")
    if user_data.username and len(user_data.username.strip()) < 3:
        raise ValidationException("Username must be at least 3 characters long")

    try:
        user = auth_service.register_user(
            session,
            user_data.email.strip().lower(),
            user_data.password,
            user_data.username.strip() if user_data.username else None,
        )

        # Record successful registration
        if metrics:
            metrics.record_user_operation("register", "success")
            metrics.record_user_registration("success", "none")
            metrics.record_api_client_request("bff", "/users", "success")
            metrics.record_database_operation("insert", "users", "success", 0.0)
            metrics.record_password_operation("hash", "success")
            metrics.record_password_strength("strong")  # Assuming strong password validation
            metrics.record_security_event("user_registration", "low")
            metrics.record_response_size("register", 300)  # Approximate user response size
            metrics.record_cache_performance("user", "miss")  # New user cache

        return user
    except ValueError as e:
        # Record registration failure
        if metrics:
            failure_reason = "validation_error"
            if "email" in str(e).lower():
                failure_reason = "email_conflict"
            elif "username" in str(e).lower():
                failure_reason = "username_conflict"

            metrics.record_user_operation("register", "failure")
            metrics.record_user_registration("failure", failure_reason)
            metrics.record_api_client_request("bff", "/users", "failure")
            metrics.record_database_operation("insert", "users", "failure", 0.0)
            metrics.record_security_event("registration_failure", "medium")
            metrics.record_password_operation("hash", "failure")

        # Convert ValueError to semantic exception - will be caught by error mapping
        error_msg = str(e).lower()
        if "email" in error_msg and "exists" in error_msg:
            raise ValueError("email already exists") from e
        elif "username" in error_msg and "exists" in error_msg:
            raise ValueError("username already exists") from e
        else:
            raise ValidationException(f"Registration failed: {str(e)}") from e


@router.get("/users/me", response_model=UserResponse)
@track_user_management
@critical_service_handler("auth-database", logger)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current authenticated user's profile.

    Used by BFF: GET /bff/v1/users/me

    This is a CRITICAL operation - user profile access must always work.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        User profile data

    Raises:
        AuthenticationException: If user is not authenticated (handled by dependency)
        ExternalServiceException: If database is unavailable (critical failure)
    """
    # Record profile access
    metrics = get_auth_metrics()
    if metrics:
        metrics.record_user_operation("profile_access", "success")
        metrics.record_api_client_request("bff", "/users/me", "success")
        metrics.record_database_operation("select", "users", "success", 0.0)
        metrics.record_session_operation("validate", "success")
        metrics.record_response_size("profile", 400)  # Approximate user profile response size
        metrics.record_cache_performance("user", "hit")  # User profile cache

    return current_user
