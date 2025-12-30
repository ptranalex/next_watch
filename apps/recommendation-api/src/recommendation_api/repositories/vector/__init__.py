"""Vector database repository for the Recommendation API.

This package provides access to vector databases for similarity search operations.
"""

from recommendation_api.repositories.vector.repository import (
    batch_store_embeddings,
    close_vector_repository,
    create_collection,
    delete_movie_embedding,
    get_collection_info,
    get_embeddings_stats,
    get_movie_embedding,
    get_vector_repository,
    search_by_movie_id,
    search_by_movie_id_with_metadata,
    search_similar_movies,
    search_similar_movies_with_metadata,
    store_movie_embedding,
)

# Define the public API
__all__ = [
    "VectorRepository",
    "create_collection",
    "store_movie_embedding",
    "search_similar_movies",
    "get_movie_embedding",
    "delete_movie_embedding",
    "get_collection_info",
    "batch_store_embeddings",
    "search_by_movie_id",
    "get_embeddings_stats",
    "get_vector_repository",
    "close_vector_repository",
    "search_similar_movies_with_metadata",
    "search_by_movie_id_with_metadata",
]

# For backward compatibility and cleaner imports, also export the repository class
from recommendation_api.repositories.vector.repository import VectorRepository
