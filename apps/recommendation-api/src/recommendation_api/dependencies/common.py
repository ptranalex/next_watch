"""Common dependencies for Recommendation API routes."""

import logging
from typing import cast

from fastapi import Request, Depends

from recommendation_api.services.backend_client import BackendClient, get_backend_client
from recommendation_api.services.movie_adapter import (
    MovieDataAdapter,
    get_movie_adapter as movie_adapter_factory,
)
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.services.vector_service import VectorService, get_vector_service

logger = logging.getLogger(__name__)


def get_backend_client_dependency() -> BackendClient:
    """Dependency to get backend client using factory function.

    Returns:
        Backend client instance
    """
    return get_backend_client()


def get_movie_adapter_dependency() -> MovieDataAdapter:
    """Dependency to get movie data adapter using factory function.

    Returns:
        Movie data adapter instance
    """
    return movie_adapter_factory()


def get_vector_service_dependency() -> VectorService:
    """Dependency to get vector service using factory function.

    Returns:
        Vector service instance
    """
    return get_vector_service()


def get_recommendation_service(
    movie_adapter: MovieDataAdapter = Depends(get_movie_adapter_dependency),
    vector_service: VectorService = Depends(get_vector_service_dependency),
) -> RecommendationService:
    """Service factory dependency for RecommendationService.

    This implements the Service Factory Pattern using FastAPI's dependency injection.
    It creates a new RecommendationService instance with properly injected dependencies.

    Args:
        movie_adapter: Movie data adapter dependency
        vector_service: Vector service dependency

    Returns:
        RecommendationService instance with injected dependencies

    Benefits:
        - Proper dependency injection (no singletons)
        - Testable (can inject mocks)
        - Clear dependency graph
        - No global state
        - No reliance on app.state
    """
    return RecommendationService(
        movie_adapter=movie_adapter,
        vector_service=vector_service,
    )


***REMOVED*** Backward compatibility aliases (deprecated - use the new _dependency functions)
def get_backend_client(request: Request) -> BackendClient:
    """Legacy dependency - deprecated, use get_backend_client_dependency instead."""
    logger.warning("get_backend_client is deprecated, use get_backend_client_dependency")
    return get_backend_client_dependency()


def get_movie_adapter(request: Request) -> MovieDataAdapter:
    """Legacy dependency - deprecated, use get_movie_adapter_dependency instead."""
    logger.warning("get_movie_adapter is deprecated, use get_movie_adapter_dependency")
    return get_movie_adapter_dependency()
