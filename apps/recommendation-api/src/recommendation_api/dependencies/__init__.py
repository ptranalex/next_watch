"""Dependencies for Recommendation API routes.

This module provides FastAPI dependency injection functions for shared services
and components used across route handlers.
"""

from .common import get_backend_client, get_movie_adapter

__all__ = ["get_backend_client", "get_movie_adapter"]
