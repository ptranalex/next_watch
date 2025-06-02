"""Vector repository for movie embeddings in the Recommendation API.

This module provides the VectorRepository class for interacting with the vector database,
along with standalone functions for backward compatibility.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from qdrant_client.http import models

from recommendation_api.config import settings
from recommendation_api.repositories.vector.client import get_qdrant_client

logger = logging.getLogger(__name__)


class VectorRepository:
    """Repository for movie embedding vectors.
    
    This class provides methods for storing, retrieving, and searching movie embeddings
    in the vector database.
    """
    
    def create_collection(
        self, 
        vector_size: int = settings.embedding_dimension,
        distance: str = "Cosine"
    ) -> bool:
        """Create the movie embeddings collection.
        
        Args:
            vector_size: Size of vectors to store
            distance: Distance metric ("Cosine", "Euclidean", "Dot")
            
        Returns:
            True if successful, False otherwise
        """
        client = get_qdrant_client()
        return client.create_collection(
            vector_size=vector_size,
            distance=distance,
        )
    
    def store_movie_embedding(
        self,
        movie_id: int,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store a movie embedding in the vector database.
        
        Args:
            movie_id: Movie ID (used as point ID)
            embedding: Movie embedding vector
            metadata: Optional metadata to store with the embedding
            
        Returns:
            True if successful, False otherwise
        """
        client = get_qdrant_client()
        
        ***REMOVED*** Prepare metadata payload
        payload = metadata or {}
        payload["movie_id"] = movie_id
        
        ***REMOVED*** Create point
        point = models.PointStruct(
            id=movie_id,
            vector=embedding,
            payload=payload,
        )
        
        return client.upsert_points([point])
    
    def search_similar_movies(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        exclude_movie_ids: Optional[List[int]] = None,
    ) -> List[Tuple[int, float]]:
        """Search for movies similar to the query embedding.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            exclude_movie_ids: Movie IDs to exclude from results
            
        Returns:
            List of tuples (movie_id, similarity_score)
        """
        client = get_qdrant_client()
        
        ***REMOVED*** Create filter to exclude specific movies if provided
        query_filter = None
        if exclude_movie_ids:
            query_filter = models.Filter(
                must_not=[
                    models.FieldCondition(
                        key="movie_id",
                        match=models.MatchAny(any=exclude_movie_ids),
                    )
                ]
            )
        
        ***REMOVED*** Search for similar vectors
        results = client.search(
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        
        ***REMOVED*** Extract movie IDs and scores
        similar_movies = []
        for result in results:
            if result.payload is not None:
                movie_id = result.payload.get("movie_id")
                if movie_id is not None:
                    similar_movies.append((int(movie_id), float(result.score)))
        
        logger.info(f"Found {len(similar_movies)} similar movies")
        return similar_movies
    
    def get_movie_embedding(self, movie_id: int) -> Optional[List[float]]:
        """Get the embedding for a specific movie.
        
        Args:
            movie_id: Movie ID
            
        Returns:
            Movie embedding vector or None if not found
        """
        client = get_qdrant_client()
        
        point = client.get_point(movie_id)
        if point and point.vector is not None:
            ***REMOVED*** Ensure we're working with a list of floats
            if isinstance(point.vector, list):
                return [float(str(x)) for x in point.vector]
            elif isinstance(point.vector, dict):
                ***REMOVED*** Handle case where vector might be in a dict format
                vector_data = point.vector.get("vector", [])
                if isinstance(vector_data, list):
                    return [float(str(x)) for x in vector_data]
        
        return None
    
    def delete_movie_embedding(self, movie_id: int) -> bool:
        """Delete a movie embedding from the vector database.
        
        Args:
            movie_id: Movie ID
            
        Returns:
            True if successful, False otherwise
        """
        client = get_qdrant_client()
        return client.delete_points([movie_id])
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the movie embeddings collection.
        
        Returns:
            Collection info dictionary or None if error
        """
        client = get_qdrant_client()
        return client.get_collection_info()
    
    def batch_store_embeddings(
        self,
        embeddings_data: List[Tuple[int, List[float], Optional[Dict[str, Any]]]],
    ) -> bool:
        """Store multiple movie embeddings in batch.
        
        Args:
            embeddings_data: List of tuples (movie_id, embedding, metadata)
            
        Returns:
            True if successful, False otherwise
        """
        client = get_qdrant_client()
        
        ***REMOVED*** Prepare points
        points = []
        for movie_id, embedding, metadata in embeddings_data:
            payload = metadata or {}
            payload["movie_id"] = movie_id
            
            point = models.PointStruct(
                id=movie_id,
                vector=embedding,
                payload=payload,
            )
            points.append(point)
        
        return client.upsert_points(points)
    
    def search_by_movie_id(
        self,
        movie_id: int,
        limit: int = 10,
        score_threshold: Optional[float] = None,
    ) -> List[Tuple[int, float]]:
        """Search for movies similar to a specific movie.
        
        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of tuples (movie_id, similarity_score)
        """
        ***REMOVED*** Get the embedding for the movie
        embedding = self.get_movie_embedding(movie_id)
        if not embedding:
            logger.warning(f"No embedding found for movie {movie_id}")
            return []
        
        ***REMOVED*** Search for similar movies, excluding the original movie
        return self.search_similar_movies(
            query_embedding=embedding,
            limit=limit + 1,  ***REMOVED*** +1 to account for excluding the original
            score_threshold=score_threshold,
            exclude_movie_ids=[movie_id],
        )[:limit]  ***REMOVED*** Limit to requested number
    
    def get_embeddings_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings.
        
        Returns:
            Statistics dictionary
        """
        info = self.get_collection_info()
        if not info:
            return {"error": "Could not retrieve collection info"}
        
        return {
            "total_embeddings": info.get("points_count", 0),
            "indexed_embeddings": info.get("indexed_vectors_count", 0),
            "collection_status": info.get("status", "unknown"),
            "vector_size": info.get("config", {}).get("vector_size", 0),
            "distance_metric": info.get("config", {}).get("distance", "unknown"),
        }


***REMOVED*** Create a singleton instance for global use
_vector_repository: Optional[VectorRepository] = None


def get_vector_repository() -> VectorRepository:
    """Get the global vector repository instance.
    
    Returns:
        VectorRepository instance
    """
    global _vector_repository
    if _vector_repository is None:
        _vector_repository = VectorRepository()
    return _vector_repository


***REMOVED*** For backward compatibility, provide standalone functions that use the singleton
def create_collection() -> bool:
    """Create the movie embeddings collection.
    
    Returns:
        True if successful, False otherwise
    """
    return get_vector_repository().create_collection()


def store_movie_embedding(
    movie_id: int,
    embedding: List[float],
    metadata: Optional[Dict[str, Any]] = None,
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
    query_embedding: List[float],
    limit: int = 10,
    score_threshold: Optional[float] = None,
    exclude_movie_ids: Optional[List[int]] = None,
) -> List[Tuple[int, float]]:
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


def get_movie_embedding(movie_id: int) -> Optional[List[float]]:
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


def get_collection_info() -> Optional[Dict[str, Any]]:
    """Get information about the movie embeddings collection.
    
    Returns:
        Collection info dictionary or None if error
    """
    return get_vector_repository().get_collection_info()


def batch_store_embeddings(
    embeddings_data: List[Tuple[int, List[float], Optional[Dict[str, Any]]]],
) -> bool:
    """Store multiple movie embeddings in batch.
    
    Args:
        embeddings_data: List of tuples (movie_id, embedding, metadata)
        
    Returns:
        True if successful, False otherwise
    """
    return get_vector_repository().batch_store_embeddings(embeddings_data)


def search_by_movie_id(
    movie_id: int,
    limit: int = 10,
    score_threshold: Optional[float] = None,
) -> List[Tuple[int, float]]:
    """Search for movies similar to a specific movie.
    
    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        
    Returns:
        List of tuples (movie_id, similarity_score)
    """
    return get_vector_repository().search_by_movie_id(movie_id, limit, score_threshold)


def get_embeddings_stats() -> Dict[str, Any]:
    """Get statistics about stored embeddings.
    
    Returns:
        Statistics dictionary
    """
    return get_vector_repository().get_embeddings_stats() 