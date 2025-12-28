"""Vector service for the Recommendation API.

This module provides a service layer for interacting with the vector database.
"""

from typing import Any

from config.logging import get_logger

from recommendation_api.repositories.vector import (
    VectorRepository,
    close_vector_repository,
    get_vector_repository,
)
from recommendation_api.services.ml_api_client import get_ml_api_client

***REMOVED*** Movie features now come from API - see movie_adapter.py

logger = get_logger(__name__)


class VectorService:
    """Service for interacting with vector database."""

    def __init__(self, vector_repository: VectorRepository | None = None):
        """Initialize the vector service.

        Args:
            vector_repository: Vector repository instance
        """
        self.repository = vector_repository or get_vector_repository()

    def ensure_collection_exists(self) -> bool:
        """Ensure the vector collection exists.

        Returns:
            True if collection exists or was created, False if error
        """
        return self.repository.create_collection()

    def get_movie_embedding(self, movie_id: int) -> list[float] | None:
        """Get the embedding for a movie.

        Args:
            movie_id: Movie ID

        Returns:
            Movie embedding vector or None if not found
        """
        return self.repository.get_movie_embedding(movie_id)

    ***REMOVED*** NOTE: This method is deprecated in favor of API-based approach
    ***REMOVED*** Movie features now come from the backend API via MovieDataAdapter
    ***REMOVED*** Vector embeddings should be generated and stored by the ML service directly
    async def generate_and_store_movie_embedding(
        self, movie_features: dict[str, Any]
    ) -> list[float] | None:
        """Generate and store an embedding for a movie using API-provided features.

        This method will:
        1. Use provided movie features (from API)
        2. Generate an embedding using the ML API
        3. Store the embedding in the vector database
        4. Return the generated embedding

        Args:
            movie_features: Movie features dict from API

        Returns:
            Generated embedding or None if generation failed
        """
        movie_id = movie_features.get("id")
        if not movie_id:
            logger.warning("No movie_id in features")
            return None

        ***REMOVED*** Generate embedding using ML API
        try:
            ml_client = get_ml_api_client()
            embedding = await ml_client.generate_movie_embedding(movie_features)
        except Exception as e:
            logger.error(f"Failed to generate embedding for movie {movie_id}: {e}")
            return None

        ***REMOVED*** Prepare metadata
        metadata = {
            "title": movie_features.get("title", ""),
            "release_year": movie_features.get("release_year"),
            "genres": movie_features.get("genres", []),
            "imdb_rating": movie_features.get("imdb_rating"),
            "movie_id": movie_id,
        }

        ***REMOVED*** Store embedding
        success = self.repository.store_movie_embedding(
            movie_id=movie_id,
            embedding=embedding,
            metadata=metadata,
        )

        if success:
            logger.info(f"Stored embedding for movie {movie_id}")
            return embedding
        else:
            logger.error(f"Failed to store embedding for movie {movie_id}")
            return None

    def find_similar_movies(
        self,
        query_embedding: list[float],
        limit: int = 10,
        min_score: float = 0.6,
        exclude_movie_ids: list[int] | None = None,
    ) -> list[tuple[int, float]]:
        """Find movies similar to a query embedding.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)
            exclude_movie_ids: Movie IDs to exclude from results

        Returns:
            List of tuples (movie_id, similarity_score)
        """
        return self.repository.search_similar_movies(
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=min_score,
            exclude_movie_ids=exclude_movie_ids,
        )

    def find_similar_movies_by_id(
        self,
        movie_id: int,
        limit: int = 10,
        min_score: float = 0.01,  ***REMOVED*** Use a much lower default threshold
    ) -> list[tuple[int, float]]:
        """Find movies similar to a specific movie by ID.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)

        Returns:
            List of tuples (movie_id, similarity_score)
        """
        logger.debug(f"Finding similar movies for movie ID {movie_id} with min_score={min_score}")

        ***REMOVED*** Delegate to repository layer, which now handles fallbacks internally
        similar_movies = self.repository.search_by_movie_id(
            movie_id=movie_id,
            limit=limit,
            score_threshold=min_score,
        )

        logger.debug(f"Found {len(similar_movies)} similar movies for movie {movie_id}")
        return similar_movies

    def get_vector_stats(self) -> dict[str, Any]:
        """Get statistics about vector database.

        Returns:
            Dictionary with statistics
        """
        stats = self.repository.get_embeddings_stats()

        ***REMOVED*** Add service-level info
        stats["service_status"] = "healthy" if stats.get("total_embeddings", 0) > 0 else "warning"

        return stats

    ***REMOVED*** NOTE: This method is deprecated - use ML service for batch processing
    ***REMOVED*** Movie data should now come from the backend API
    def batch_process_movies_deprecated(
        self,
        movie_features_list: list[dict[str, Any]],
        force: bool = False,
    ) -> dict[str, Any]:
        """DEPRECATED: Process multiple movies in batch, generating and storing embeddings.

        This method is deprecated in favor of using the ML service directly
        for batch processing of embeddings.

        Args:
            movie_features_list: List of movie features from API
            force: Force regeneration of existing embeddings

        Returns:
            Dictionary with processing results
        """
        logger.warning("batch_process_movies is deprecated - use ML service for batch processing")

        results = {
            "total": len(movie_features_list),
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "deprecated": True,
        }

        return results

    def find_similar_movies_with_metadata(
        self,
        query_embedding: list[float],
        limit: int = 10,
        min_score: float = 0.6,
        exclude_movie_ids: list[int] | None = None,
    ) -> list[tuple[int, float, dict[str, Any]]]:
        """Find movies similar to a query embedding with metadata.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)
            exclude_movie_ids: Movie IDs to exclude from results

        Returns:
            List of tuples (movie_id, similarity_score, metadata)
        """
        return self.repository.search_similar_movies_with_metadata(
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=min_score,
            exclude_movie_ids=exclude_movie_ids,
        )

    def find_similar_movies_by_id_with_metadata(
        self,
        movie_id: int,
        limit: int = 10,
        min_score: float = 0.01,  ***REMOVED*** Use a much lower default threshold
    ) -> list[tuple[int, float, dict[str, Any]]]:
        """Find movies similar to a specific movie by ID with metadata.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)

        Returns:
            List of tuples (movie_id, similarity_score, metadata)
        """
        logger.debug(
            f"Finding similar movies with metadata for movie ID {movie_id} with min_score={min_score}"
        )

        ***REMOVED*** Delegate to repository layer, which handles fallbacks internally
        similar_movies = self.repository.search_by_movie_id_with_metadata(
            movie_id=movie_id,
            limit=limit,
            score_threshold=min_score,
        )

        logger.debug(
            f"Found {len(similar_movies)} similar movies with metadata for movie {movie_id}"
        )
        return similar_movies

    async def close(self) -> None:
        """Close the vector service and release resources."""
        ***REMOVED*** Currently, no async resources to close in the service itself
        ***REMOVED*** But we'll keep this method async for future compatibility
        pass


***REMOVED*** Global vector service instance
_vector_service: VectorService | None = None


def get_vector_service() -> VectorService:
    """Get or create a global vector service instance.

    Returns:
        VectorService instance
    """
    global _vector_service

    if _vector_service is None:
        _vector_service = VectorService()

    return _vector_service


async def close_vector_service() -> None:
    """Close the global vector service and release resources."""
    global _vector_service

    if _vector_service is not None:
        await _vector_service.close()
        _vector_service = None

    ***REMOVED*** Close the underlying vector repository
    await close_vector_repository()
