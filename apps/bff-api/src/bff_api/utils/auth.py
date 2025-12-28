"""Authentication utilities for BFF API."""

import jwt
from config.logging import get_logger

from bff_api.config.app import settings

logger = get_logger(__name__)


def extract_user_id_from_token(token: str, raise_on_invalid: bool = True) -> int | None:
    """Extract user ID from JWT token.

    Args:
        token: JWT access token
        raise_on_invalid: Whether to raise an exception for invalid tokens (default: True)

    Returns:
        User ID if token is valid

    Raises:
        AuthenticationException: If token is invalid and raise_on_invalid=True
    """
    try:
        ***REMOVED*** Use the JWT secret from our settings
        ***REMOVED*** Fall back to auth service default if not configured
        jwt_secret = settings.jwt_secret or "change_this_in_production_very_important"

        logger.debug(
            "Attempting to decode JWT token",
            has_secret=bool(jwt_secret),
            token_length=len(token),
            service="bff",
            component="auth",
        )

        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        logger.debug(
            "Successfully decoded JWT payload",
            payload_keys=list(payload.keys()),
            service="bff",
            component="auth",
        )

        ***REMOVED*** Extract user ID from 'sub' claim
        sub = payload.get("sub")
        if sub is None:
            error_msg = "Token payload missing 'sub' claim"
            logger.warning(
                error_msg,
                available_keys=list(payload.keys()),
                service="bff",
                component="auth",
            )
            if raise_on_invalid:
                from fast_core.errors.exceptions import AuthenticationException

                raise AuthenticationException(
                    detail="Invalid token: missing user identification",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        logger.debug(
            "Successfully extracted user_id from token",
            user_id=sub,
            service="bff",
            component="auth",
        )
        return int(sub)

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired", service="bff", component="auth")
        if raise_on_invalid:
            from fast_core.errors.exceptions import AuthenticationException

            raise AuthenticationException(
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid JWT token", error=str(e), service="bff", component="auth")
        if raise_on_invalid:
            from fast_core.errors.exceptions import AuthenticationException

            raise AuthenticationException(
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    except (ValueError, Exception) as e:
        logger.warning(
            "Failed to extract user ID from token",
            error=str(e),
            service="bff",
            component="auth",
        )
        if raise_on_invalid:
            from fast_core.errors.exceptions import AuthenticationException

            raise AuthenticationException(
                detail="Token processing error",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None


def extract_user_id_from_token_lenient(token: str) -> int | None:
    """Extract user ID from JWT token with lenient error handling.

    This function silently fails and returns None for invalid tokens.
    Use this ONLY for legacy compatibility where silent failure is required.

    For new code, use extract_user_id_from_token() which properly raises exceptions.

    Args:
        token: JWT access token

    Returns:
        User ID if token is valid, None otherwise (no exceptions raised)
    """
    return extract_user_id_from_token(token, raise_on_invalid=False)
