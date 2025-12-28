"""
User database operations module.

This module provides functions for managing user records in the database.
"""

import logging
from typing import Any

from sqlmodel import Session, select

from movie_storage.models.user import User

logger = logging.getLogger(__name__)


def create_user(
    session: Session,
    email: str,
    password: str,
    username: str | None = None,
) -> User:
    """
    Create a new user in the database.

    Args:
        session: SQLModel database session
        email: User email address
        password: Plaintext password (will be hashed)
        username: Optional username

    Returns:
        Newly created User object

    Raises:
        ValueError: If a user with the email already exists
    """
    ***REMOVED*** Check if user with email already exists
    existing_user = get_user_by_email(session, email)
    if existing_user:
        raise ValueError(f"User with email {email} already exists")

    ***REMOVED*** Create new user with hashed password
    hashed_password = User.hash_password(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        username=username,
    )

    ***REMOVED*** Add to database
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"Created new user with email: {email}")
    return user


def get_user_by_id(session: Session, user_id: int) -> User | None:
    """
    Get a user by ID.

    Args:
        session: SQLModel database session
        user_id: User ID to look up

    Returns:
        User if found, None otherwise
    """
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Get a user by email address.

    Args:
        session: SQLModel database session
        email: Email address to look up

    Returns:
        User if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    results = session.exec(statement)
    return results.first()


def get_user_by_username(session: Session, username: str) -> User | None:
    """
    Get a user by username.

    Args:
        session: SQLModel database session
        username: Username to look up

    Returns:
        User if found, None otherwise
    """
    statement = select(User).where(User.username == username)
    results = session.exec(statement)
    return results.first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get a list of users, with pagination.

    Args:
        session: SQLModel database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of User objects
    """
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement))


def update_user(
    session: Session,
    user_id: int,
    data: dict[str, Any],
) -> User | None:
    """
    Update user data.

    Args:
        session: SQLModel database session
        user_id: ID of the user to update
        data: Dictionary of fields to update

    Returns:
        Updated User if found and updated, None otherwise
    """
    user = get_user_by_id(session, user_id)
    if not user:
        return None

    ***REMOVED*** Handle password updates
    if "password" in data:
        data["hashed_password"] = User.hash_password(data.pop("password"))

    ***REMOVED*** Update user attributes
    for key, value in data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"Updated user with ID: {user_id}")
    return user


def delete_user(session: Session, user_id: int) -> bool:
    """
    Delete a user.

    Args:
        session: SQLModel database session
        user_id: ID of the user to delete

    Returns:
        True if user was found and deleted, False otherwise
    """
    user = get_user_by_id(session, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()

    logger.info(f"Deleted user with ID: {user_id}")
    return True


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user with email and password.

    Args:
        session: SQLModel database session
        email: User email address
        password: Plaintext password to check

    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_email(session, email)

    if not user:
        logger.warning(f"Authentication failed: No user found with email {email}")
        return None

    if not user.verify_password(password):
        logger.warning(f"Authentication failed: Invalid password for {email}")
        return None

    logger.info(f"User {email} authenticated successfully")
    return user
