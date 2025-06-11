"""
API routes module.

This module contains API route handlers for different API versions.
"""

from .v1 import (
    movies_router as movies_router_v1,
    actors_router as actors_router_v1,
    search_router as search_router_v1,
    user_interactions_router as user_interactions_router_v1,
)

__all__ = [
    "movies_router_v1",
    "actors_router_v1",
    "search_router_v1",
    "user_interactions_router_v1",
]
