"""Authentication utilities for BFF API."""

from typing import Optional
import jwt
from bff_api.config.app import settings
from bff_api.config.logging import get_logger

logger = get_logger("bff_api.utils.auth")


def extract_user_id_from_token(token: str) -> Optional[int]:
    """Extract user ID from JWT token.

    Args:
        token: JWT access token

    Returns:
        User ID if token is valid, None otherwise
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
            logger.warning(
                "Token payload missing 'sub' claim",
                available_keys=list(payload.keys()),
                service="bff",
                component="auth",
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
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid JWT token", error=str(e), service="bff", component="auth")
        return None
    except (ValueError, Exception) as e:
        logger.warning(
            "Failed to extract user ID from token", error=str(e), service="bff", component="auth"
        )
        return None
