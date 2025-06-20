"""Common dependencies for Recommendation API routes."""

import logging
from typing import cast

from fastapi import Request

from recommendation_api.services.backend_client import BackendClient
from recommendation_api.services.movie_adapter import MovieDataAdapter
from recommendation_api.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)


def get_backend_client(request: Request) -> BackendClient:
    """Dependency to get backend client from app state.

    Args:
        request: FastAPI request object

    Returns:
        Shared backend client instance

    Raises:
        AttributeError: If backend client is not initialized in app state
    """
    return cast(BackendClient, request.app.state.backend_client)


def get_movie_adapter(request: Request) -> MovieDataAdapter:
    """Dependency to get movie data adapter from app state.

    Args:
        request: FastAPI request object

    Returns:
        Shared movie data adapter instance

    Raises:
        AttributeError: If movie adapter is not initialized in app state
    """
    return cast(MovieDataAdapter, request.app.state.movie_adapter)


def get_recommendation_service(request: Request) -> RecommendationService:
    """Dependency to get recommendation service with movie adapter.

    Args:
        request: FastAPI request object

    Returns:
        RecommendationService instance

    Raises:
        AttributeError: If movie adapter is not initialized in app state
    """
    movie_adapter = cast(MovieDataAdapter, request.app.state.movie_adapter)
    return RecommendationService(movie_adapter)
