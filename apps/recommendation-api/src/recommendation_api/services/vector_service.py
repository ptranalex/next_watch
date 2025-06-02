"""Vector service for the Recommendation API.

This module provides high-level vector operations for the recommendation engine,
separating business logic from data access.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session

from recommendation_api.repositories.vector import VectorRepository, get_vector_repository
from recommendation_api.services.embedding import generate_movie_embedding
from recommendation_api.db.operations import get_movie_features

logger = logging.getLogger(__name__)


class VectorService:
    """Service for vector operations.
    
    This service provides high-level operations for managing and using vector embeddings
    in the recommendation engine.
    """

    def __init__(self, vector_repository: Optional[VectorRepository] = None):
        """Initialize the vector service.
        
        Args:
            vector_repository: Vector repository to use (defaults to global instance)
        """
        self.repository = vector_repository or get_vector_repository()
    
    def ensure_collection_exists(self) -> bool:
        """Ensure the vector collection exists, creating it if necessary.
        
        Returns:
            True if collection exists or was created, False otherwise
        """
        return self.repository.create_collection()
    
    def get_movie_embedding(self, movie_id: int) -> Optional[List[float]]:
        """Get embedding for a movie.
        
        If the embedding doesn't exist in the database, this method returns None.
        
        Args:
            movie_id: Movie ID
            
        Returns:
            Movie embedding vector or None if not found
        """
        return self.repository.get_movie_embedding(movie_id)
    
    def generate_and_store_movie_embedding(
        self, 
        session: Session, 
        movie_id: int
    ) -> Optional[List[float]]:
        """Generate and store an embedding for a movie.
        
        This method will:
        1. Get movie features from the database
        2. Generate an embedding using those features
        3. Store the embedding in the vector database
        4. Return the generated embedding
        
        Args:
            session: Database session
            movie_id: Movie ID
            
        Returns:
            Generated embedding or None if movie features not found
        """
        ***REMOVED*** Get movie features
        features = get_movie_features(session, movie_id)
        if not features:
            logger.warning(f"No features found for movie {movie_id}")
            return None
        
        ***REMOVED*** Generate embedding
        embedding = generate_movie_embedding(features)
        
        ***REMOVED*** Prepare metadata
        metadata = {
            "title": features.get("title", ""),
            "release_year": features.get("release_year"),
            "genres": features.get("genres", []),
            "imdb_rating": features.get("imdb_rating"),
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
        query_embedding: List[float],
        limit: int = 10,
        min_score: float = 0.7,
        exclude_movie_ids: Optional[List[int]] = None,
    ) -> List[Tuple[int, float]]:
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
        min_score: float = 0.7,
    ) -> List[Tuple[int, float]]:
        """Find movies similar to a specific movie by ID.
        
        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of tuples (movie_id, similarity_score)
        """
        return self.repository.search_by_movie_id(
            movie_id=movie_id,
            limit=limit,
            score_threshold=min_score,
        )
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get statistics about vector database.
        
        Returns:
            Dictionary with statistics
        """
        stats = self.repository.get_embeddings_stats()
        
        ***REMOVED*** Add service-level info
        stats["service_status"] = "healthy" if stats.get("total_embeddings", 0) > 0 else "warning"
        
        return stats
    
    def batch_process_movies(
        self, 
        session: Session,
        movie_ids: List[int],
    ) -> Dict[str, Any]:
        """Process multiple movies in batch, generating and storing embeddings.
        
        Args:
            session: Database session
            movie_ids: List of movie IDs to process
            
        Returns:
            Dictionary with processing results
        """
        results = {
            "total": len(movie_ids),
            "processed": 0,
            "failed": 0,
            "skipped": 0,
        }
        
        ***REMOVED*** Ensure collection exists
        if not self.ensure_collection_exists():
            logger.error("Failed to ensure collection exists")
            results["error"] = "Failed to ensure collection exists"
            return results
        
        ***REMOVED*** Process movies
        embeddings_data = []
        
        for movie_id in movie_ids:
            ***REMOVED*** Check if embedding already exists
            existing_embedding = self.repository.get_movie_embedding(movie_id)
            if existing_embedding:
                results["skipped"] += 1
                continue
            
            ***REMOVED*** Get movie features
            features = get_movie_features(session, movie_id)
            if not features:
                logger.warning(f"No features found for movie {movie_id}")
                results["failed"] += 1
                continue
            
            ***REMOVED*** Generate embedding
            embedding = generate_movie_embedding(features)
            
            ***REMOVED*** Prepare metadata
            metadata = {
                "title": features.get("title", ""),
                "release_year": features.get("release_year"),
                "genres": features.get("genres", []),
                "imdb_rating": features.get("imdb_rating"),
            }
            
            ***REMOVED*** Add to batch
            embeddings_data.append((movie_id, embedding, metadata))
        
        ***REMOVED*** Store batch
        if embeddings_data:
            success = self.repository.batch_store_embeddings(embeddings_data)
            if success:
                results["processed"] = len(embeddings_data)
                logger.info(f"Processed {len(embeddings_data)} movies in batch")
            else:
                results["failed"] += len(embeddings_data)
                logger.error("Failed to store batch embeddings")
        
        return results


***REMOVED*** Singleton instance
_vector_service: Optional[VectorService] = None


def get_vector_service() -> VectorService:
    """Get the global vector service instance.
    
    Returns:
        VectorService instance
    """
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service 