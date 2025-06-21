"""JWT utilities for FastAPI applications.

This module provides JWT (JSON Web Token) utilities for authentication
and authorization in FastAPI applications.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from jwt import PyJWTError
from pydantic import BaseModel, Field

from config.logging import get_logger

logger = get_logger(__name__)


class JWTConfig(BaseModel):
    """JWT configuration model."""

    secret_key: str = Field(..., description="Secret key for JWT signing")
    algorithm: str = Field("HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration in days")
    issuer: Optional[str] = Field(None, description="JWT issuer")
    audience: Optional[str] = Field(None, description="JWT audience")


class TokenData(BaseModel):
    """Token data model."""

    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    iss: Optional[str] = Field(None, description="Issuer")
    aud: Optional[str] = Field(None, description="Audience")
    jti: Optional[str] = Field(None, description="JWT ID")
    type: str = Field("access", description="Token type (access/refresh)")
    scope: Optional[str] = Field(None, description="Token scope")


class JWTManager:
    """JWT token manager."""

    def __init__(self, config: JWTConfig):
        """Initialize JWT manager.

        Args:
            config: JWT configuration
        """
        self.config = config

    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        scope: Optional[str] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create access token.

        Args:
            subject: Token subject (usually user ID)
            expires_delta: Token expiration time delta
            scope: Token scope
            additional_claims: Additional claims to include

        Returns:
            Encoded JWT token string
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.access_token_expire_minutes
            )

        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "type": "access",
        }

        if self.config.issuer:
            payload["iss"] = self.config.issuer

        if self.config.audience:
            payload["aud"] = self.config.audience

        if scope:
            payload["scope"] = scope

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

    def create_refresh_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create refresh token.

        Args:
            subject: Token subject (usually user ID)
            expires_delta: Token expiration time delta
            additional_claims: Additional claims to include

        Returns:
            Encoded JWT refresh token string
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self.config.refresh_token_expire_days
            )

        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32),  ***REMOVED*** Unique token ID for refresh tokens
        }

        if self.config.issuer:
            payload["iss"] = self.config.issuer

        if self.config.audience:
            payload["aud"] = self.config.audience

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

    def verify_token(
        self,
        token: str,
        expected_type: str = "access",
    ) -> TokenData:
        """Verify and decode JWT token.

        Args:
            token: JWT token string
            expected_type: Expected token type (access/refresh)

        Returns:
            TokenData with decoded claims

        Raises:
            PyJWTError: If token is invalid
            ValueError: If token type doesn't match expected
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                audience=self.config.audience,
            )
        except PyJWTError as e:
            logger.debug(f"JWT verification failed: {e}")
            raise

        ***REMOVED*** Check token type
        token_type = payload.get("type", "access")
        if token_type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type}, got {token_type}")

        return TokenData(**payload)

    def refresh_access_token(
        self,
        refresh_token: str,
        new_scope: Optional[str] = None,
    ) -> str:
        """Create new access token from refresh token.

        Args:
            refresh_token: Valid refresh token
            new_scope: Optional new scope for access token

        Returns:
            New access token string

        Raises:
            PyJWTError: If refresh token is invalid
            ValueError: If token is not a refresh token
        """
        token_data = self.verify_token(refresh_token, expected_type="refresh")

        return self.create_access_token(
            subject=token_data.sub,
            scope=new_scope,
        )

    def get_token_subject(self, token: str) -> str:
        """Get subject from token without full verification.

        Args:
            token: JWT token string

        Returns:
            Token subject

        Raises:
            PyJWTError: If token is malformed
        """
        ***REMOVED*** Decode without verification for subject extraction
        payload = jwt.decode(token, options={"verify_signature": False})
        return str(payload.get("sub", ""))

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired.

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False otherwise
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            if not exp:
                return True
            return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
        except Exception:
            return True

    def decode_token_payload(self, token: str) -> Dict[str, Any]:
        """Decode token payload without verification.

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            PyJWTError: If token is malformed
        """
        payload = jwt.decode(token, options={"verify_signature": False})
        return dict(payload)


def generate_secret_key() -> str:
    """Generate a secure secret key for JWT signing.

    Returns:
        Base64 encoded secret key
    """
    return secrets.token_urlsafe(64)


def create_jwt_manager(
    secret_key: Optional[str] = None,
    algorithm: str = "HS256",
    access_token_expire_minutes: int = 30,
    refresh_token_expire_days: int = 7,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
) -> JWTManager:
    """Create JWT manager with configuration.

    Args:
        secret_key: Secret key for JWT signing (generates random if None)
        algorithm: JWT signing algorithm
        access_token_expire_minutes: Access token expiration in minutes
        refresh_token_expire_days: Refresh token expiration in days
        issuer: JWT issuer
        audience: JWT audience

    Returns:
        Configured JWTManager instance
    """
    if not secret_key:
        secret_key = generate_secret_key()
        logger.warning("Using auto-generated secret key. This should not be used in production.")

    config = JWTConfig(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
        refresh_token_expire_days=refresh_token_expire_days,
        issuer=issuer,
        audience=audience,
    )

    return JWTManager(config)
