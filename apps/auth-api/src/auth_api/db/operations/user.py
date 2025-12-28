"""
User database operations for the auth API.
"""

from datetime import datetime

from config.logging import get_logger

***REMOVED*** Import enhanced error handling
from fast_core.errors import (
    ValidationException,
    critical_service_handler,
)
from sqlmodel import Session, select

from auth_api.models.user import User

logger = get_logger(__name__)


@critical_service_handler("auth-database", logger, error_mapping={ValueError: lambda e: e})
def create_user(
    session: Session,
    email: str,
    password: str,
    username: str | None = None,
) -> User:
    """
    Create a new user with hashed password.

    This is a CRITICAL operation for user registration.

    Args:
        session: Database session
        email: User's email address
        password: User's plaintext password
        username: Optional username

    Returns:
        Created user instance

    Raises:
        ValueError: If email already exists or validation fails (will be mapped to semantic exceptions)
        ExternalServiceException: If database is unavailable (critical failure)
    """
    ***REMOVED*** Check if user with email already exists
    existing_user = get_user_by_email(session, email)
    if existing_user:
        raise ValueError(f"User with email {email} already exists")

    ***REMOVED*** Check if username already exists (if provided)
    if username:
        existing_username = get_user_by_username(session, username)
        if existing_username:
            raise ValueError(f"User with username {username} already exists")

    ***REMOVED*** Hash the password
    hashed_password = User.hash_password(password)

    ***REMOVED*** Create new user
    user = User(
        email=email,
        hashed_password=hashed_password,
        username=username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@critical_service_handler("auth-database", logger)
def get_user_by_id(session: Session, user_id: int) -> User | None:
    """
    Get a user by their ID.

    This is a CRITICAL operation used throughout the authentication system.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        User instance if found, None otherwise

    Raises:
        ExternalServiceException: If database is unavailable (critical failure)
    """
    return session.get(User, user_id)


@critical_service_handler("auth-database", logger)
def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Get a user by their email address.

    This is a CRITICAL operation for authentication and registration.

    Args:
        session: Database session
        email: User's email address

    Returns:
        User instance if found, None otherwise

    Raises:
        ExternalServiceException: If database is unavailable (critical failure)
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


@critical_service_handler("auth-database", logger)
def get_user_by_username(session: Session, username: str) -> User | None:
    """
    Get a user by their username.

    This is a CRITICAL operation for username validation during registration.

    Args:
        session: Database session
        username: User's username

    Returns:
        User instance if found, None otherwise

    Raises:
        ExternalServiceException: If database is unavailable (critical failure)
    """
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


@critical_service_handler("auth-database", logger)
def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get multiple users with pagination.

    This is a CRITICAL operation for user management.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of user instances

    Raises:
        ValidationException: If pagination parameters are invalid
        ExternalServiceException: If database is unavailable (critical failure)
    """
    ***REMOVED*** Validate pagination parameters
    if skip < 0:
        raise ValidationException("Skip parameter must be non-negative")
    if limit <= 0 or limit > 1000:
        raise ValidationException("Limit must be between 1 and 1000")

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return list(users)


@critical_service_handler("auth-database", logger, error_mapping={ValueError: lambda e: e})
def update_user(
    session: Session,
    user_id: int,
    email: str | None = None,
    password: str | None = None,
    username: str | None = None,
) -> User | None:
    """
    Update a user's information.

    This is a CRITICAL operation for user profile management.

    Args:
        session: Database session
        user_id: User's ID
        email: New email address (optional)
        password: New password (optional)
        username: New username (optional)

    Returns:
        Updated user instance if found, None otherwise

    Raises:
        ValueError: If email or username already exists (will be mapped to semantic exceptions)
        ExternalServiceException: If database is unavailable (critical failure)
    """
    user = session.get(User, user_id)
    if not user:
        return None

    ***REMOVED*** Check for email conflicts if email is being updated
    if email and email != user.email:
        existing_user = get_user_by_email(session, email)
        if existing_user and existing_user.id != user_id:
            raise ValueError(f"User with email {email} already exists")
        user.email = email

    ***REMOVED*** Check for username conflicts if username is being updated
    if username and username != user.username:
        existing_user = get_user_by_username(session, username)
        if existing_user and existing_user.id != user_id:
            raise ValueError(f"User with username {username} already exists")
        user.username = username

    ***REMOVED*** Update password if provided
    if password:
        user.hashed_password = User.hash_password(password)

    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@critical_service_handler("auth-database", logger)
def delete_user(session: Session, user_id: int) -> bool:
    """
    Delete a user by their ID.

    This is a CRITICAL operation for user account deletion.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        True if user was deleted, False if user not found

    Raises:
        ExternalServiceException: If database is unavailable (critical failure)
    """
    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True


@critical_service_handler("auth-database", logger)
def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.

    This is a CRITICAL operation for user login functionality.

    Args:
        session: Database session
        email: User's email address
        password: User's plaintext password

    Returns:
        User instance if authentication successful, None otherwise

    Raises:
        ExternalServiceException: If database is unavailable (critical failure)
    """
    user = get_user_by_email(session, email)
    if not user:
        return None

    if not user.verify_password(password):
        return None

    return user
