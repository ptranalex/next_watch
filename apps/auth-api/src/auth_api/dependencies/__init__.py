"""Shared dependencies for Auth API routes.

This module exports common dependencies used across auth API routes.
"""

# Import auth service dependencies
from .auth import get_auth_service, get_current_user

# Import database dependencies
from .database import get_db

__all__ = [
    # Auth service dependencies
    "get_auth_service",
    "get_current_user",
    # Database dependencies
    "get_db",
]
