"""Authentication utilities for BFF API."""

import logging
from typing import Optional
import jwt
from bff_api.config.app import settings

logger = logging.getLogger(__name__)


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
        
        logger.debug(f"🔑 Using JWT secret: {'***' if jwt_secret else 'None'}")
        logger.debug(f"🔍 Token length: {len(token)}")
        
        payload = jwt.decode(
            token, 
            jwt_secret, 
            algorithms=["HS256"]
        )
        
        logger.debug(f"🔓 Successfully decoded JWT payload: {list(payload.keys())}")
        
        ***REMOVED*** Extract user ID from 'sub' claim
        sub = payload.get("sub")
        if sub is None:
            logger.warning("Token payload missing 'sub' claim")
            logger.debug(f"🔍 Available payload keys: {list(payload.keys())}")
            return None
            
        logger.debug(f"✅ Successfully extracted user_id: {sub}")
        return int(sub)
        
    except jwt.ExpiredSignatureError:
        logger.warning("🕐 Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"❌ Invalid token: {e}")
        return None
    except (ValueError, Exception) as e:
        logger.warning(f"❌ Failed to extract user ID from token: {e}")
        return None 