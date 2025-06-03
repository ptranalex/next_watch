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
        
        ***REMOVED*** First try the direct retrieval approach with vectors explicitly requested
        point = client.get_point(movie_id, with_vectors=True)
        logger.debug(f"Retrieved point for movie {movie_id}: point exists: {point is not None}")
        
        if point:
            logger.debug(f"Point has vector attribute: {hasattr(point, 'vector')}, Vector is None: {point.vector is None}")
            
            if hasattr(point, 'payload'):
                logger.debug(f"Point payload: {point.payload}")
            
            if point.vector is not None:
                ***REMOVED*** Ensure we're working with a list of floats
                if isinstance(point.vector, list):
                    logger.debug(f"Vector is a list with {len(point.vector)} elements")
                    return [float(str(x)) for x in point.vector]
                elif isinstance(point.vector, dict):
                    ***REMOVED*** Handle case where vector might be in a dict format
                    logger.debug(f"Vector is a dict: {point.vector}")
                    vector_data = point.vector.get("vector", [])
                    if isinstance(vector_data, list):
                        logger.debug(f"Vector data from dict has {len(vector_data)} elements")
                        return [float(str(x)) for x in vector_data]
        
        ***REMOVED*** If point exists but vector is None, or any other issue with direct retrieval,
        ***REMOVED*** try using the search method with filtering as fallback
        if point and point.vector is None:
            logger.debug(f"Point for movie {movie_id} exists but vector is None, trying fallback approach")
            
            ***REMOVED*** Search for the point by movie_id using our wrapper
            from recommendation_api.config import settings
            from qdrant_client.http import models
            
            ***REMOVED*** Use a dummy vector for search, actual similarity won't matter since we're filtering exactly
            vector_size = settings.embedding_dimension
            dummy_vector = [0.1] * vector_size
            
            ***REMOVED*** Search for exactly this movie ID
            try:
                results = client.search(
                    query_vector=dummy_vector,
                    query_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="movie_id",
                                match=models.MatchValue(value=movie_id)
                            )
                        ]
                    ),
                    limit=1
                )
                
                logger.debug(f"Search fallback found {len(results)} results")
                
                if results and len(results) > 0:
                    ***REMOVED*** If we found the result via search, it should have vector data
                    first_result = results[0]
                    logger.debug(f"First result has vector: {hasattr(first_result, 'vector')}, Vector is None: {first_result.vector is None if hasattr(first_result, 'vector') else 'N/A'}")
                    
                    if hasattr(first_result, 'vector') and first_result.vector is not None:
                        logger.info(f"Successfully retrieved vector for movie {movie_id} via search fallback")
                        return [float(str(x)) for x in first_result.vector]
            except Exception as e:
                logger.error(f"Error in fallback search for movie {movie_id}: {e}")
        
        logger.warning(f"No embedding found for movie {movie_id} with any method")
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
        """Store multiple movie embeddings in batch using repository.
        
        Args:
            embeddings_data: List of tuples (movie_id, embedding, metadata)
            
        Returns:
            True if successful, False otherwise
        """
        client = get_qdrant_client()
        
        points = []
        for movie_id, embedding, metadata in embeddings_data:
            ***REMOVED*** Prepare metadata payload
            payload = metadata or {}
            payload["movie_id"] = movie_id
            
            ***REMOVED*** Create point
            point = models.PointStruct(
                id=movie_id,
                vector=embedding,
                payload=payload,
            )
            points.append(point)
        
        return client.upsert_points(points)
    
    def upsert_batch(
        self,
        embeddings_data: List[Dict[str, Any]],
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
            movie_id = item['id']
            embedding = item['vector']
            metadata = item.get('metadata', {})
            
            ***REMOVED*** Ensure movie_id is in metadata
            metadata["movie_id"] = movie_id
            
            ***REMOVED*** Create point
            point = models.PointStruct(
                id=movie_id,
                vector=embedding,
                payload=metadata,
            )
            points.append(point)
        
        ***REMOVED*** Use wait=true to ensure all points are properly indexed
        return client.client.upsert(
            collection_name=client.collection_name,
            points=points,
            wait=True
        ) is not None
    
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
        
        ***REMOVED*** If embedding is successfully retrieved, use standard similarity search
        if embedding:
            logger.debug(f"Found embedding for movie {movie_id}, using standard similarity search")
            return self.search_similar_movies(
                query_embedding=embedding,
                limit=limit + 1,  ***REMOVED*** +1 to account for excluding the original
                score_threshold=score_threshold,
                exclude_movie_ids=[movie_id],
            )[:limit]  ***REMOVED*** Limit to requested number
        
        ***REMOVED*** If embedding retrieval failed, try direct search with filtering
        logger.warning(f"No embedding found for movie {movie_id}, using fallback search approach")
        
        ***REMOVED*** Get Qdrant client
        client = get_qdrant_client()
        
        ***REMOVED*** Check if the movie exists in the database first
        point = client.get_point(movie_id)
        if not point:
            logger.warning(f"Movie {movie_id} not found in vector database")
            return []
        
        ***REMOVED*** If movie exists but vector couldn't be retrieved, use fallback approach
        try:
            ***REMOVED*** Use a dummy vector to search and filter by movie_id
            from recommendation_api.config import settings
            from qdrant_client.http import models
            
            ***REMOVED*** Use a random-ish vector as query (exact values don't matter)
            vector_size = settings.embedding_dimension
            dummy_vector = [0.1] * vector_size
            
            ***REMOVED*** Search for all other movies, excluding this one
            similar_response = client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=dummy_vector,
                query_filter=models.Filter(
                    must_not=[
                        models.FieldCondition(
                            key="movie_id",
                            match=models.MatchValue(value=movie_id)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=score_threshold
            )
            
            if similar_response:
                ***REMOVED*** Convert to our standard format
                results = [(int(point.id), float(point.score)) for point in similar_response]
                logger.debug(f"Found {len(results)} similar movies with fallback approach")
                return results
            
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
        
        ***REMOVED*** If all approaches failed
        return []
    
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
    """Store multiple movie embeddings in batch using repository.
    
    Args:
        embeddings_data: List of tuples (movie_id, embedding, metadata)
        
    Returns:
        True if successful, False otherwise
    """
    repo = get_vector_repository()
    return repo.batch_store_embeddings(embeddings_data)


def upsert_batch(
    embeddings_data: List[Dict[str, Any]],
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