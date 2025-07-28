"""
Authentication service for JWT-based user authentication in dedicated auth service.
"""

from config.logging import get_logger
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, cast

import jwt
from sqlmodel import Session

from auth_api.config.app import settings
from auth_api.schemas.auth_schemas import TokenVerificationResponse
from auth_api.models.user import User
from auth_api.db.operations.user import (
    authenticate_user,
    get_user_by_id,
    create_user,
)

***REMOVED*** Import enhanced error handling
from fast_core.errors import (
    critical_service_handler,
    service_error_handler,
    ValidationException,
    AuthenticationException,
    ExternalServiceException,
)

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service for JWT token generation and validation.

    Dedicated service for centralized authentication in microservices architecture.
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
        self.access_token_expire_minutes = self.config.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = self.config.jwt_refresh_token_expire_days

        if not self.jwt_secret:
            raise ValueError("JWT_SECRET must be set in environment")

    def create_access_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User ID to encode in the token
            expires_delta: Optional custom expiration delta

        Returns:
            JWT access token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt

    def create_refresh_token(self, user_id: int) -> str:
        """
        Create a JWT refresh token.

        Args:
            user_id: User ID to encode in the token

        Returns:
            JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt

    @service_error_handler(
        service_name="jwt-service",
        logger=logger,
        preserve_semantics=True,
        error_mapping={
            "expired": lambda e: AuthenticationException("Token has expired"),
            "invalid": lambda e: AuthenticationException("Invalid token"),
            "malformed": lambda e: AuthenticationException("Malformed token"),
        },
    )
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token payload

        Raises:
            AuthenticationException: If token is invalid or expired (preserves semantic meaning)
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return cast(Dict[str, Any], payload)
        except jwt.ExpiredSignatureError as e:
            logger.warning(f"Token has expired: {str(e)}")
            raise ValueError("expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise ValueError("invalid")
        except Exception as e:
            logger.warning(f"Failed to decode token: {str(e)}")
            raise ValueError("malformed")

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
        except (AuthenticationException, ValueError) as e:
            logger.warning(f"Failed to extract user ID from token: {str(e)}")
            return None

    @critical_service_handler("auth-database", logger)
    def verify_token(self, session: Session, token: str) -> TokenVerificationResponse:
        """
        Verify token and return user information for BFF service.

        This is the key method used by BFF to validate tokens from frontend.
        This is a CRITICAL operation that must always work for the platform to function.

        Args:
            session: Database session
            token: JWT token to verify

        Returns:
            TokenVerificationResponse with user info or error

        Raises:
            ExternalServiceException: If database is unavailable (critical failure)
        """
        try:
            ***REMOVED*** Decode and validate token
            payload = self.decode_token(token)

            ***REMOVED*** Extract user ID
            sub = payload.get("sub")
            if sub is None:
                return TokenVerificationResponse(valid=False, error="Token missing user identifier")

            user_id = int(sub)

            ***REMOVED*** Get user from database
            user = get_user_by_id(session, user_id)
            if not user:
                return TokenVerificationResponse(valid=False, error="User not found")

            ***REMOVED*** Return successful verification with user info
            return TokenVerificationResponse(
                valid=True, user_id=user.id, email=user.email, username=user.username
            )

        except AuthenticationException as e:
            ***REMOVED*** Token validation errors are expected and should not be treated as system failures
            error_msg = str(e)
            if "expired" in error_msg.lower():
                return TokenVerificationResponse(valid=False, error="Token has expired")
            elif "invalid" in error_msg.lower():
                return TokenVerificationResponse(valid=False, error="Invalid token")
            else:
                return TokenVerificationResponse(valid=False, error="Token verification failed")
        except (ValueError, Exception) as e:
            logger.error(f"Token verification error: {str(e)}")
            return TokenVerificationResponse(valid=False, error="Token verification failed")

    @critical_service_handler("auth-database", logger)
    def authenticate(self, session: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        This is a CRITICAL operation for user login functionality.

        Args:
            session: Database session
            email: User's email
            password: User's password

        Returns:
            User object if authentication successful, None otherwise

        Raises:
            ExternalServiceException: If database is unavailable (critical failure)
        """
        return authenticate_user(session, email, password)

    @critical_service_handler("auth-database", logger)
    def get_user_by_token(self, session: Session, token: str) -> Optional[User]:
        """
        Get user by JWT token.

        This is a CRITICAL operation used for protected endpoints.

        Args:
            session: Database session
            token: JWT token

        Returns:
            User object if token is valid, None otherwise

        Raises:
            ExternalServiceException: If database is unavailable (critical failure)
        """
        user_id = self.get_user_id_from_token(token)
        if not user_id:
            return None

        return get_user_by_id(session, user_id)

    @critical_service_handler("auth-database", logger)
    def register_user(
        self,
        session: Session,
        email: str,
        password: str,
        username: Optional[str] = None,
    ) -> User:
        """
        Register a new user.

        This is a CRITICAL operation for user onboarding.

        Args:
            session: Database session
            email: User's email
            password: User's password
            username: Optional username

        Returns:
            Newly created User object

        Raises:
            ValueError: If registration fails (will be mapped to semantic exceptions)
            ExternalServiceException: If database is unavailable (critical failure)
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
            ***REMOVED*** Decode the refresh token
            payload = self.decode_token(refresh_token)

            ***REMOVED*** Verify it's a refresh token
            if payload.get("type") != "refresh":
                logger.warning("Invalid token type for refresh operation")
                return None

            ***REMOVED*** Extract user ID
            user_id_str = payload.get("sub")
            if not user_id_str:
                logger.warning("Refresh token missing user ID")
                return None

            user_id = int(user_id_str)

            ***REMOVED*** Generate new tokens
            return self.generate_tokens(user_id)

        except (AuthenticationException, ValueError) as e:
            logger.warning(f"Failed to refresh tokens: {str(e)}")
            return None
