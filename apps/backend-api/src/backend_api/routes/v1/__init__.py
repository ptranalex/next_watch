"""
API routes version 1.

This module contains the version 1 API route handlers.
"""

from .auth import router as auth_router
from .movies import router as movies_router
from .actors import router as actors_router
from .search import router as search_router
from .user_interactions import router as user_interactions_router

__all__ = [
    "auth_router",
    "movies_router",
    "actors_router",
    "search_router",
    "user_interactions_router",
]
