"""API routes for embedding generation."""

from typing import Any, Callable

from config.logging import get_logger
from fastapi import APIRouter, HTTPException

from ml_api.core.metrics import get_ml_metrics
from ml_api.models import (
    ModelInfo,
    MovieEmbeddingRequest,
    MovieEmbeddingResponse,
    UserEmbeddingRequest,
    UserEmbeddingResponse,
)
from ml_api.services import embedding_service


def _default_active_embedding_service() -> Any:
    """Default embedding service provider (can be overridden at runtime)."""
    return embedding_service


***REMOVED*** This can be overridden by app wiring if another implementation is available.
get_active_embedding_service: Callable[[], Any] = _default_active_embedding_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/embeddings", tags=["embeddings"])


@router.post("/movie", response_model=MovieEmbeddingResponse)
async def generate_movie_embedding(request: MovieEmbeddingRequest) -> MovieEmbeddingResponse:
    """Generate an embedding for a movie."""
    ***REMOVED*** Record metrics
    metrics = get_ml_metrics()
    if metrics:
        metrics.record_embedding_request("movie", 1)  ***REMOVED*** Single movie embedding

    try:
        logger.info(f"Generating embedding for movie {request.movie_id}")

        ***REMOVED*** Get the active service
        active_service = get_active_embedding_service()

        result = active_service.generate_movie_embedding(
            movie_id=request.movie_id,
            title=request.title,
            overview=request.overview,
            genres=request.genres,
            additional_metadata=request.additional_metadata,
        )

        ***REMOVED*** Record successful embedding generation
        if metrics:
            metrics.record_embedding_duration(
                "movie", 0.0
            )  ***REMOVED*** Duration would be tracked by decorator

        return MovieEmbeddingResponse(
            movie_id=result["movie_id"],
            embedding=result["embedding"],
            model_id=result["model_id"],
            dimensions=result["dimensions"],
        )

    except Exception as e:
        logger.error(f"Error generating movie embedding: {e}")
        ***REMOVED*** Record embedding error
        if metrics:
            metrics.record_embedding_error("movie", "generation_failed")
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e!s}") from e


@router.post("/user", response_model=UserEmbeddingResponse)
async def generate_user_embedding(request: UserEmbeddingRequest) -> UserEmbeddingResponse:
    """Generate a preference vector for a user."""
    ***REMOVED*** Record metrics
    metrics = get_ml_metrics()
    batch_size = len(request.liked_movies)
    if metrics:
        metrics.record_embedding_request("user", batch_size)

    try:
        logger.info(f"Generating preference vector for user {request.user_id}")

        ***REMOVED*** Convert liked_movies to the format expected by the service
        liked_movies = [
            {"movie_id": movie.movie_id, "rating": movie.rating} for movie in request.liked_movies
        ]

        ***REMOVED*** Get the active service
        active_service = get_active_embedding_service()

        result = active_service.generate_user_preference_vector(
            user_id=request.user_id,
            liked_movies=liked_movies,
            watched_genres=request.watched_genres,
        )

        ***REMOVED*** Record successful embedding generation
        if metrics:
            metrics.record_embedding_duration("user", 0.0)  ***REMOVED*** Duration would be tracked by decorator
            metrics.record_embedding_batch_size("user", batch_size)

        return UserEmbeddingResponse(
            user_id=result["user_id"],
            preference_vector=result["preference_vector"],
            model_id=result["model_id"],
            dimensions=result["dimensions"],
        )

    except Exception as e:
        logger.error(f"Error generating user preference vector: {e}")
        ***REMOVED*** Record embedding error
        if metrics:
            metrics.record_embedding_error("user", "generation_failed")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate preference vector: {e!s}"
        ) from e


@router.get("/info", response_model=ModelInfo)
async def get_model_info() -> ModelInfo:
    """Get information about the embedding model."""
    ***REMOVED*** Record metrics
    metrics = get_ml_metrics()
    if metrics:
        metrics.record_embedding_request("info", 1)

    try:
        ***REMOVED*** Get the active service
        active_service = get_active_embedding_service()
        model_info = active_service.get_model_info()

        ***REMOVED*** Record successful model info retrieval
        if metrics:
            metrics.record_embedding_duration("info", 0.0)  ***REMOVED*** Duration would be tracked by decorator

        return ModelInfo(**model_info)

    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        ***REMOVED*** Record embedding error
        if metrics:
            metrics.record_embedding_error("info", "info_retrieval_failed")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {e!s}") from e
