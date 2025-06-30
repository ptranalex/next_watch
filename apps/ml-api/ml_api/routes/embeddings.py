"""API routes for embedding generation."""

import logging
import os
from typing import Any, Callable

from fastapi import APIRouter, HTTPException

from ml_api.models import (
    ModelInfo,
    MovieEmbeddingRequest,
    MovieEmbeddingResponse,
    UserEmbeddingRequest,
    UserEmbeddingResponse,
)
from ml_api.services import embedding_service

***REMOVED*** This will be overridden by app.py if precomputed service is available
get_active_embedding_service: Callable[[], Any] = lambda: embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/embeddings", tags=["embeddings"])


@router.post("/movie", response_model=MovieEmbeddingResponse)
async def generate_movie_embedding(request: MovieEmbeddingRequest) -> MovieEmbeddingResponse:
    """Generate an embedding for a movie."""
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

        return MovieEmbeddingResponse(
            movie_id=result["movie_id"],
            embedding=result["embedding"],
            model_id=result["model_id"],
            dimensions=result["dimensions"],
        )

    except Exception as e:
        logger.error(f"Error generating movie embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")


@router.post("/user", response_model=UserEmbeddingResponse)
async def generate_user_embedding(request: UserEmbeddingRequest) -> UserEmbeddingResponse:
    """Generate a preference vector for a user."""
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

        return UserEmbeddingResponse(
            user_id=result["user_id"],
            preference_vector=result["preference_vector"],
            model_id=result["model_id"],
            dimensions=result["dimensions"],
        )

    except Exception as e:
        logger.error(f"Error generating user preference vector: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate preference vector: {str(e)}"
        )


@router.get("/info", response_model=ModelInfo)
async def get_model_info() -> ModelInfo:
    """Get information about the embedding model."""
    try:
        ***REMOVED*** Get the active service
        active_service = get_active_embedding_service()
        model_info = active_service.get_model_info()
        return ModelInfo(**model_info)

    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")
