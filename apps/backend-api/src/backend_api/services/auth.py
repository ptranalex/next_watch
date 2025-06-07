"""
Authentication service for JWT-based user authentication.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast

import jwt
from movie_storage.db.operations.user import (
    authenticate_user,
    create_user,
    get_user_by_id,
)
from movie_storage.models.user import User
from sqlmodel import Session

***REMOVED*** Use absolute import to avoid mypy errors
import backend_api.config.app
from backend_api.config.app import settings

***REMOVED*** Use relative imports instead
from ..config import app
from ..config.app import settings

***REMOVED*** Use relative imports for better type checking
from ..config import app
from ..config.app import settings

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service for JWT token generation and validation.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize the authentication service.

        Args:
            config: Configuration instance
        """
        self.config = config or settings
        ***REMOVED*** Get JWT settings from config
        self.jwt_secret = self.config.jwt_secret
        self.jwt_algorithm = self.config.jwt_algorithm
        self.access_token_expire_minutes = self.config.access_token_expire_minutes
        self.refresh_token_expire_days = self.config.refresh_token_expire_days

        if not self.jwt_secret:
            raise ValueError("JWT_SECRET must be set in environment")

    def create_access_token(self, user_id: int) -> str:
        """
        Create a JWT access token for the given user ID.

        Args:
            user_id: User ID to encode in the token

        Returns:
            JWT access token as string
        """
        ***REMOVED*** Set expiration time
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expire = datetime.utcnow() + expires_delta

        ***REMOVED*** Create token payload
        payload = {
            "sub": str(user_id),  ***REMOVED*** subject (user identifier)
            "exp": expire,  ***REMOVED*** expiration time
            "iat": datetime.utcnow(),  ***REMOVED*** issued at
            "type": "access",  ***REMOVED*** token type
        }

        ***REMOVED*** Encode token
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

        ***REMOVED*** Cast to string to satisfy mypy
        return token

    def create_refresh_token(self, user_id: int) -> str:
        """
        Create a JWT refresh token for the given user ID.

        Args:
            user_id: User ID to encode in the token

        Returns:
            JWT refresh token as string
        """
        ***REMOVED*** Set expiration time (longer than access token)
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        expire = datetime.utcnow() + expires_delta

        ***REMOVED*** Create token payload
        payload = {
            "sub": str(user_id),  ***REMOVED*** subject (user identifier)
            "exp": expire,  ***REMOVED*** expiration time
            "iat": datetime.utcnow(),  ***REMOVED*** issued at
            "type": "refresh",  ***REMOVED*** token type
        }

        ***REMOVED*** Encode token
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

        ***REMOVED*** Cast to string to satisfy mypy
        return token

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token payload

        Raises:
            jwt.PyJWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return cast(Dict[str, Any], payload)
        except jwt.PyJWTError as e:
            logger.warning(f"Failed to decode token: {str(e)}")
            raise

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract user ID from token.

        Args:
            token: JWT token

        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = self.decode_token(token)
            sub = payload.get("sub")
            if sub is None:
                logger.warning("Token payload missing 'sub' claim")
                return None

            user_id = int(sub)
            return user_id
        except (jwt.PyJWTError, ValueError) as e:
            logger.warning(f"Failed to extract user ID from token: {str(e)}")
            return None

    def authenticate(self, session: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            session: Database session
            email: User's email
            password: User's password

        Returns:
            User object if authentication successful, None otherwise
        """
        return authenticate_user(session, email, password)

    def get_user_by_token(self, session: Session, token: str) -> Optional[User]:
        """
        Get user by JWT token.

        Args:
            session: Database session
            token: JWT token

        Returns:
            User object if token is valid, None otherwise
        """
        user_id = self.get_user_id_from_token(token)
        if not user_id:
            return None

        return get_user_by_id(session, user_id)

    def register_user(
        self,
        session: Session,
        email: str,
        password: str,
        username: Optional[str] = None,
    ) -> User:
        """
        Register a new user.

        Args:
            session: Database session
            email: User's email
            password: User's password
            username: Optional username

        Returns:
            Newly created User object

        Raises:
            ValueError: If registration fails
        """
        return create_user(session, email, password, username)

    def generate_tokens(self, user_id: int) -> Dict[str, str]:
        """
        Generate both access and refresh tokens for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with access_token and refresh_token
        """
        return {
            "access_token": self.create_access_token(user_id),
            "refresh_token": self.create_refresh_token(user_id),
            "token_type": "bearer",
        }

    def refresh_tokens(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Generate new tokens using a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token pair if refresh token is valid, None otherwise
        """
        try:
            payload = self.decode_token(refresh_token)

            ***REMOVED*** Verify this is a refresh token
            if payload.get("type") != "refresh":
                logger.warning("Attempted to use non-refresh token for refresh")
                return None

            ***REMOVED*** Get user ID and generate new tokens
            sub = payload.get("sub")
            if sub is None:
                logger.warning("Refresh token payload missing 'sub' claim")
                return None

            user_id = int(sub)
            return self.generate_tokens(user_id)

        except (jwt.PyJWTError, ValueError) as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return None
