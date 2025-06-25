"""Shared dependencies for Auth API routes.

This module exports common dependencies used across auth API routes.
"""

***REMOVED*** Import auth service dependencies
from .auth import get_auth_service, get_current_user

***REMOVED*** Import database dependencies
from .database import get_db

__all__ = [
    ***REMOVED*** Auth service dependencies
    "get_auth_service",
    "get_current_user",
    ***REMOVED*** Database dependencies
    "get_db",
]
