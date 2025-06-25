"""
User database operations for the auth API.
"""

from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from auth_api.models.user import User


def create_user(
    session: Session,
    email: str,
    password: str,
    username: Optional[str] = None,
) -> User:
    """
    Create a new user with hashed password.

    Args:
        session: Database session
        email: User's email address
        password: User's plaintext password
        username: Optional username

    Returns:
        Created user instance

    Raises:
        ValueError: If email already exists or validation fails
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


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """
    Get a user by their ID.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        User instance if found, None otherwise
    """
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address.

    Args:
        session: Database session
        email: User's email address

    Returns:
        User instance if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """
    Get a user by their username.

    Args:
        session: Database session
        username: User's username

    Returns:
        User instance if found, None otherwise
    """
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_users(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """
    Get a list of users with pagination.

    Args:
        session: Database session
        skip: Number of users to skip
        limit: Maximum number of users to return

    Returns:
        List of users
    """
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_user(
    session: Session,
    user_id: int,
    email: Optional[str] = None,
    password: Optional[str] = None,
    username: Optional[str] = None,
) -> Optional[User]:
    """
    Update a user's information.

    Args:
        session: Database session
        user_id: User's ID
        email: New email address (optional)
        password: New password (optional)
        username: New username (optional)

    Returns:
        Updated user instance if found, None otherwise

    Raises:
        ValueError: If email or username already exists
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


def delete_user(session: Session, user_id: int) -> bool:
    """
    Delete a user by their ID.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        True if user was deleted, False if user not found
    """
    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.

    Args:
        session: Database session
        email: User's email address
        password: User's plaintext password

    Returns:
        User instance if authentication successful, None otherwise
    """
    user = get_user_by_email(session, email)
    if not user:
        return None

    if not user.verify_password(password):
        return None

    return user
