"""Data models for the ML API."""

from ml_api.models.embedding import (
    ModelInfo,
    MovieEmbeddingRequest,
    MovieEmbeddingResponse,
    UserEmbeddingRequest,
    UserEmbeddingResponse,
    UserMovieRating,
)

__all__ = [
    "MovieEmbeddingRequest",
    "MovieEmbeddingResponse",
    "UserMovieRating",
    "UserEmbeddingRequest",
    "UserEmbeddingResponse",
    "ModelInfo",
]
