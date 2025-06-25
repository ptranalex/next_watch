"""
API routes version 1.

This module contains the version 1 API route handlers.
"""

from .actors import router as actors_router
from .genres import router as genres_router
from .movies import router as movies_router
from .search import router as search_router
from .user_collections import router as user_collections_router

__all__ = [
    "movies_router",
    "actors_router",
    "genres_router",
    "search_router",
    "user_collections_router",
]
