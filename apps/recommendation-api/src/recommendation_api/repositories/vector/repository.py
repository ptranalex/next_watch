"""Vector repository for movie embeddings in the Recommendation API.

This module provides the VectorRepository class for interacting with the vector database,
along with standalone functions for backward compatibility.
"""

import time
from typing import Any, cast

from config.logging import get_logger
from qdrant_client.http import models

from recommendation_api.config import settings
from recommendation_api.repositories.vector.client import (
    QdrantClient,
    close_qdrant_client,
    get_qdrant_client,
)

logger = get_logger(__name__)


class VectorRepository:
    """Repository for movie embedding vectors.

    This class provides methods for storing, retrieving, and searching movie embeddings
    in the vector database.
    """

    def __init__(self, client: QdrantClient | None = None):
        """Initialize the vector repository.

        Args:
            client: Qdrant client instance
        """
        self.client = client or get_qdrant_client()
        self.collection_name = settings.qdrant_collection_name

    def create_collection(
        self, vector_size: int = settings.embedding_dimension, distance: str = "Cosine"
    ) -> bool:
        """Create the movie embeddings collection.

        Args:
            vector_size: Size of vectors to store
            distance: Distance metric ("Cosine", "Euclidean", "Dot")

        Returns:
            True if successful, False otherwise
        """
        return self.client.create_collection(
            collection_name=self.collection_name,
            vector_size=vector_size,
            distance=distance,
        )

    def store_movie_embedding(
        self,
        movie_id: int,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Store a movie embedding in the vector database.

        Args:
            movie_id: Movie ID (used as point ID)
            embedding: Movie embedding vector
            metadata: Optional metadata to store with the embedding

        Returns:
            True if successful, False otherwise
        """
        if not embedding:
            logger.warning(f"Empty embedding for movie {movie_id}")
            return False

        # Ensure collection exists
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' does not exist, creating...")
            if not self.create_collection():
                logger.error(f"Failed to create collection '{self.collection_name}'")
                return False

        # Prepare payload with metadata and version info
        payload = metadata or {}

        # Add metadata version to track schema changes
        payload["metadata_version"] = "v2"

        # Add timestamp for tracking
        payload["indexed_at"] = time.time()

        # Create point
        point = models.PointStruct(
            id=movie_id,
            vector=embedding,
            payload=payload,
        )

        # Upsert point
        return self.client.upsert_points(
            points=[point],
            collection_name=self.collection_name,
        )

    def search_similar_movies(
        self,
        query_embedding: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
        exclude_movie_ids: list[int] | None = None,
    ) -> list[tuple[int, float]]:
        """Search for movies similar to the query embedding.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            exclude_movie_ids: Movie IDs to exclude from results

        Returns:
            List of tuples (movie_id, similarity_score)
        """
        # Create filter to exclude specific movie IDs if needed
        query_filter = None
        if exclude_movie_ids and len(exclude_movie_ids) > 0:
            query_filter = models.Filter(
                must_not=[
                    models.FieldCondition(
                        key="id",
                        match=models.MatchAny(any=exclude_movie_ids),
                    )
                ]
            )

        try:
            # Search for similar vectors
            search_results = self.client.search(
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                collection_name=self.collection_name,
                query_filter=query_filter,
            )

            # Extract movie IDs and scores
            similar_movies = [(int(result.id), result.score) for result in search_results]

            logger.debug(f"Found {len(similar_movies)} similar movies")
            return similar_movies

        except Exception as e:
            logger.error(f"Error searching for similar movies: {e}")
            return []

    def get_movie_embedding(self, movie_id: int) -> list[float] | None:
        """Get the embedding for a specific movie.

        Args:
            movie_id: Movie ID

        Returns:
            Movie embedding vector or None if not found
        """
        try:
            point = self.client.get_point(
                point_id=movie_id,
                collection_name=self.collection_name,
                with_vectors=True,
            )

            if point and point.vector:
                return cast(list[float], point.vector)
            else:
                logger.debug(f"No embedding found for movie {movie_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting embedding for movie {movie_id}: {e}")
            return None

    def delete_movie_embedding(self, movie_id: int) -> bool:
        """Delete a movie embedding from the vector database.

        Args:
            movie_id: Movie ID

        Returns:
            True if successful, False otherwise
        """
        return self.client.delete_points(
            point_ids=[movie_id],
            collection_name=self.collection_name,
        )

    def get_collection_info(self) -> dict[str, Any] | None:
        """Get information about the movie embeddings collection.

        Returns:
            Collection info dictionary or None if error
        """
        return self.client.get_collection_info(collection_name=self.collection_name)

    def batch_store_embeddings(
        self,
        embeddings_data: list[tuple[int, list[float], dict[str, Any] | None]],
    ) -> bool:
        """Store multiple movie embeddings in batch using repository.

        Args:
            embeddings_data: List of tuples (movie_id, embedding, metadata)

        Returns:
            True if successful, False otherwise
        """
        if not embeddings_data:
            return False

        # Ensure collection exists
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' does not exist, creating...")
            if not self.create_collection():
                logger.error(f"Failed to create collection '{self.collection_name}'")
                return False

        points = []
        for movie_id, embedding, metadata in embeddings_data:
            if not embedding:
                logger.warning(f"Empty embedding for movie {movie_id}, skipping")
                continue

            # Add metadata version and timestamp
            payload = (metadata or {}).copy()
            payload["metadata_version"] = "v2"
            payload["indexed_at"] = time.time()

            # Create point
            point = models.PointStruct(
                id=movie_id,
                vector=embedding,
                payload=payload,
            )
            points.append(point)

        if not points:
            return False

        # Batch upsert
        return self.client.upsert_points(
            points=points,
            collection_name=self.collection_name,
        )

    def upsert_batch(
        self,
        embeddings_data: list[dict[str, Any]],
    ) -> bool:
        """Store multiple movie embeddings in batch using repository with improved format.

        Args:
            embeddings_data: List of dicts with keys 'id', 'vector', and 'metadata'

        Returns:
            True if successful, False otherwise
        """
        client = get_qdrant_client()

        points = []
        for item in embeddings_data:
            movie_id = item["id"]
            embedding = item["vector"]
            metadata = item.get("metadata", {})

            # Ensure movie_id is in metadata
            metadata["movie_id"] = movie_id

            # Create point
            point = models.PointStruct(
                id=movie_id,
                vector=embedding,
                payload=metadata,
            )
            points.append(point)

        # Use wait=true to ensure all points are properly indexed
        return (
            client.client.upsert(collection_name=client.collection_name, points=points, wait=True)
            is not None
        )

    def search_by_movie_id(
        self,
        movie_id: int,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[tuple[int, float]]:
        """Search for movies similar to a specific movie.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of tuples (movie_id, similarity_score)
        """
        # Get the embedding for the movie
        embedding = self.get_movie_embedding(movie_id)

        # If embedding is successfully retrieved, use standard similarity search
        if embedding:
            logger.debug(f"Found embedding for movie {movie_id}, using standard similarity search")
            return self.search_similar_movies(
                query_embedding=embedding,
                limit=limit + 1,  # +1 to account for excluding the original
                score_threshold=score_threshold,
                exclude_movie_ids=[movie_id],
            )[:limit]  # Limit to requested number

        # If embedding retrieval failed, try direct search with filtering
        logger.warning(f"No embedding found for movie {movie_id}, using fallback search approach")

        # Get Qdrant client
        client = get_qdrant_client()

        # Check if the movie exists in the database first
        point = client.get_point(movie_id)
        if not point:
            logger.warning(f"Movie {movie_id} not found in vector database")
            return []

        # If movie exists but vector couldn't be retrieved, use fallback approach
        try:
            # Use a dummy vector to search and filter by movie_id
            from qdrant_client.http import models

            from recommendation_api.config import settings

            # Use a random-ish vector as query (exact values don't matter)
            vector_size = settings.embedding_dimension
            dummy_vector = [0.1] * vector_size

            # Search for all other movies, excluding this one
            similar_response = client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=dummy_vector,
                query_filter=models.Filter(
                    must_not=[
                        models.FieldCondition(
                            key="movie_id", match=models.MatchValue(value=movie_id)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=score_threshold,
            )

            if similar_response:
                # Convert to our standard format
                results = [(int(point.id), float(point.score)) for point in similar_response]
                logger.debug(f"Found {len(results)} similar movies with fallback approach")
                return results

        except Exception as e:
            logger.error(f"Error in fallback search: {e}")

        # If all approaches failed
        return []

    def get_embeddings_stats(self) -> dict[str, Any]:
        """Get statistics about stored embeddings.

        Returns:
            Statistics dictionary
        """
        stats: dict[str, Any] = {
            "total_embeddings": 0,
            "collection_exists": False,
        }

        # Check if collection exists
        if not self.client.collection_exists(self.collection_name):
            return stats

        stats["collection_exists"] = True

        # Get collection info
        collection_info = self.get_collection_info()
        if collection_info:
            stats["total_embeddings"] = collection_info.get("vectors_count", 0)
            stats["points_count"] = collection_info.get("points_count", 0)
            stats["indexed_vectors_count"] = collection_info.get("indexed_vectors_count", 0)
            stats["segments_count"] = collection_info.get("segments_count", 0)

            # Add config info if available
            config = collection_info.get("config", {})
            if config:
                stats["vector_size"] = config.get("vector_size")
                stats["distance"] = config.get("distance")

        return stats

    def search_similar_movies_with_metadata(
        self,
        query_embedding: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
        exclude_movie_ids: list[int] | None = None,
    ) -> list[tuple[int, float, dict[str, Any]]]:
        """Search for movies similar to the query embedding with metadata.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            exclude_movie_ids: Movie IDs to exclude from results

        Returns:
            List of tuples (movie_id, similarity_score, metadata)
        """
        # Create filter to exclude specific movie IDs if needed
        query_filter = None
        if exclude_movie_ids and len(exclude_movie_ids) > 0:
            query_filter = models.Filter(
                must_not=[
                    models.FieldCondition(
                        key="id",
                        match=models.MatchAny(any=exclude_movie_ids),
                    )
                ]
            )

        try:
            # Search for similar vectors
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Since we can't get payload directly, fetch it separately for each result
            similar_movies = []

            for result in search_results:
                movie_id = int(result.id)
                score = result.score

                # Get the point with payload
                try:
                    point = self.client.get_point(
                        collection_name=self.collection_name,
                        point_id=movie_id,
                    )
                    payload = point.payload if point and getattr(point, "payload", None) else {}
                except Exception as e:
                    logger.warning(f"Error getting payload for movie {movie_id}: {e}")
                    payload = {}

                similar_movies.append((movie_id, score, payload))

            logger.debug(f"Found {len(similar_movies)} similar movies with metadata")
            return similar_movies

        except Exception as e:
            logger.error(f"Error searching for similar movies with metadata: {e}")
            return []

    def search_by_movie_id_with_metadata(
        self,
        movie_id: int,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[tuple[int, float, dict[str, Any]]]:
        """Search for movies similar to a specific movie with metadata.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of tuples (movie_id, similarity_score, metadata)
        """
        # Get the embedding for the movie
        embedding = self.get_movie_embedding(movie_id)

        # If embedding is successfully retrieved, use enhanced similarity search
        if embedding:
            logger.debug(f"Found embedding for movie {movie_id}, using metadata similarity search")
            return self.search_similar_movies_with_metadata(
                query_embedding=embedding,
                limit=limit + 1,  # +1 to account for excluding the original
                score_threshold=score_threshold,
                exclude_movie_ids=[movie_id],
            )[:limit]  # Limit to requested number

        # If embedding retrieval failed, fallback to old approach
        logger.warning(f"No embedding found for movie {movie_id}, falling back to standard search")

        # Fallback to standard search and then fetch metadata separately
        standard_results = self.search_by_movie_id(movie_id, limit, score_threshold)

        # Convert to metadata format by fetching individual payloads
        client = get_qdrant_client()
        results_with_metadata = []

        for similar_movie_id, score in standard_results:
            try:
                point = client.get_point(similar_movie_id)  # Payload is included by default
                if point and point.payload:
                    metadata = {
                        "id": similar_movie_id,
                        "title": point.payload.get("title", ""),
                        "overview": point.payload.get("overview"),
                        "release_date": point.payload.get("release_date"),
                        "imdb_rating": point.payload.get("imdb_rating"),
                        "vote_average": point.payload.get("tmdb_rating"),
                        "poster_url": point.payload.get("poster_url"),
                        "backdrop_url": point.payload.get("backdrop_url"),
                        "runtime": point.payload.get("runtime"),
                        "imdb_id": point.payload.get("imdb_id"),
                        "original_title": point.payload.get("original_title"),
                        "language": point.payload.get("language"),
                        "popularity": point.payload.get("popularity"),
                        "vote_count": point.payload.get("vote_count"),
                        "adult": point.payload.get("adult", False),
                        "metacritic_rating": point.payload.get("metacritic_rating"),
                        "rotten_tomatoes_rating": point.payload.get("rotten_tomatoes_rating"),
                        "awards": point.payload.get("awards"),
                        "genres": (
                            [{"name": genre} for genre in point.payload.get("genres", [])]
                            if point.payload.get("genres")
                            else []
                        ),
                        "metadata_version": point.payload.get("metadata_version", "v1"),
                    }
                    results_with_metadata.append((similar_movie_id, score, metadata))
                else:
                    # If no metadata available, skip this result
                    logger.warning(f"No metadata found for movie {similar_movie_id}, skipping")
            except Exception as e:
                logger.warning(f"Error fetching metadata for movie {similar_movie_id}: {e}")

        return results_with_metadata

    async def close(self) -> None:
        """Close the repository and release resources."""
        # Currently, no async resources to close in the repository itself
        # But we'll keep this method async for future compatibility
        pass


# Create a singleton instance for global use
_vector_repository: VectorRepository | None = None


def get_vector_repository() -> VectorRepository:
    """Get or create a global vector repository instance.

    Returns:
        VectorRepository instance
    """
    global _vector_repository

    if _vector_repository is None:
        _vector_repository = VectorRepository()

    return _vector_repository


# For backward compatibility, provide standalone functions that use the singleton
def create_collection() -> bool:
    """Create the movie embeddings collection.

    Returns:
        True if successful, False otherwise
    """
    return get_vector_repository().create_collection()


def store_movie_embedding(
    movie_id: int,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Store a movie embedding in the vector database.

    Args:
        movie_id: Movie ID (used as point ID)
        embedding: Movie embedding vector
        metadata: Optional metadata to store with the embedding

    Returns:
        True if successful, False otherwise
    """
    return get_vector_repository().store_movie_embedding(movie_id, embedding, metadata)


def search_similar_movies(
    query_embedding: list[float],
    limit: int = 10,
    score_threshold: float | None = None,
    exclude_movie_ids: list[int] | None = None,
) -> list[tuple[int, float]]:
    """Search for movies similar to the query embedding.

    Args:
        query_embedding: Query embedding vector
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        exclude_movie_ids: Movie IDs to exclude from results

    Returns:
        List of tuples (movie_id, similarity_score)
    """
    return get_vector_repository().search_similar_movies(
        query_embedding, limit, score_threshold, exclude_movie_ids
    )


def get_movie_embedding(movie_id: int) -> list[float] | None:
    """Get the embedding for a specific movie.

    Args:
        movie_id: Movie ID

    Returns:
        Movie embedding vector or None if not found
    """
    return get_vector_repository().get_movie_embedding(movie_id)


def delete_movie_embedding(movie_id: int) -> bool:
    """Delete a movie embedding from the vector database.

    Args:
        movie_id: Movie ID

    Returns:
        True if successful, False otherwise
    """
    return get_vector_repository().delete_movie_embedding(movie_id)


def get_collection_info() -> dict[str, Any] | None:
    """Get information about the movie embeddings collection.

    Returns:
        Collection info dictionary or None if error
    """
    return get_vector_repository().get_collection_info()


def batch_store_embeddings(
    embeddings_data: list[tuple[int, list[float], dict[str, Any] | None]],
) -> bool:
    """Store multiple movie embeddings in batch using repository.

    Args:
        embeddings_data: List of tuples (movie_id, embedding, metadata)

    Returns:
        True if successful, False otherwise
    """
    repo = get_vector_repository()
    return repo.batch_store_embeddings(embeddings_data)


def upsert_batch(
    embeddings_data: list[dict[str, Any]],
) -> bool:
    """Store multiple movie embeddings in batch using repository with improved format.

    Args:
        embeddings_data: List of dicts with keys 'id', 'vector', and 'metadata'

    Returns:
        True if successful, False otherwise
    """
    repo = get_vector_repository()
    return repo.upsert_batch(embeddings_data)


def search_by_movie_id(
    movie_id: int,
    limit: int = 10,
    score_threshold: float | None = None,
) -> list[tuple[int, float]]:
    """Search for movies similar to a specific movie.

    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of results
        score_threshold: Minimum similarity score

    Returns:
        List of tuples (movie_id, similarity_score)
    """
    return get_vector_repository().search_by_movie_id(movie_id, limit, score_threshold)


def get_embeddings_stats() -> dict[str, Any]:
    """Get statistics about stored embeddings.

    Returns:
        Statistics dictionary
    """
    return get_vector_repository().get_embeddings_stats()


def search_similar_movies_with_metadata(
    query_embedding: list[float],
    limit: int = 10,
    score_threshold: float | None = None,
    exclude_movie_ids: list[int] | None = None,
) -> list[tuple[int, float, dict[str, Any]]]:
    """Search for movies similar to the query embedding with metadata.

    Args:
        query_embedding: Query embedding vector
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        exclude_movie_ids: Movie IDs to exclude from results

    Returns:
        List of tuples (movie_id, similarity_score, metadata)
    """
    return get_vector_repository().search_similar_movies_with_metadata(
        query_embedding, limit, score_threshold, exclude_movie_ids
    )


def search_by_movie_id_with_metadata(
    movie_id: int,
    limit: int = 10,
    score_threshold: float | None = None,
) -> list[tuple[int, float, dict[str, Any]]]:
    """Search for movies similar to a specific movie with metadata.

    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of results
        score_threshold: Minimum similarity score

    Returns:
        List of tuples (movie_id, similarity_score, metadata)
    """
    return get_vector_repository().search_by_movie_id_with_metadata(
        movie_id, limit, score_threshold
    )


async def close_vector_repository() -> None:
    """Close the global vector repository and release resources."""
    global _vector_repository

    if _vector_repository is not None:
        await _vector_repository.close()
        _vector_repository = None

    # Close the underlying Qdrant client
    close_qdrant_client()
