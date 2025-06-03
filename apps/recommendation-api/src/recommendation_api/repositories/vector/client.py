"""Qdrant vector database client for the Recommendation API service."""

import logging
from typing import Optional, List, Dict, Any, Union
from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException

from recommendation_api.config import settings

logger = logging.getLogger(__name__)

***REMOVED*** Global client instance
_qdrant_client: Optional["QdrantClient"] = None


class QdrantClient:
    """Wrapper for Qdrant client with recommendation-specific methods."""
    
    def __init__(self, client: QdrantClientBase):
        """Initialize with a Qdrant client instance.
        
        Args:
            client: Qdrant client instance
        """
        self.client = client
        self.collection_name = settings.qdrant_collection_name
        
    def test_connection(self) -> bool:
        """Test connection to Qdrant.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            collections = self.client.get_collections()
            logger.info(f"Qdrant connection successful. Found {len(collections.collections)} collections")
            return True
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            return False
    
    def collection_exists(self, collection_name: Optional[str] = None) -> bool:
        """Check if collection exists.
        
        Args:
            collection_name: Collection name (defaults to configured collection)
            
        Returns:
            True if collection exists, False otherwise
        """
        name = collection_name or self.collection_name
        try:
            collections = self.client.get_collections()
            return any(col.name == name for col in collections.collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False
    
    def create_collection(
        self,
        collection_name: Optional[str] = None,
        vector_size: int = 384,
        distance: str = "Cosine",
    ) -> bool:
        """Create a new collection.
        
        Args:
            collection_name: Collection name (defaults to configured collection)
            vector_size: Size of vectors to store
            distance: Distance metric ("Cosine", "Euclidean", "Dot")
            
        Returns:
            True if successful, False otherwise
        """
        name = collection_name or self.collection_name
        
        try:
            if self.collection_exists(name):
                logger.info(f"Collection '{name}' already exists")
                return True
            
            ***REMOVED*** Map distance string to Qdrant distance enum
            distance_map = {
                "Cosine": models.Distance.COSINE,
                "Euclidean": models.Distance.EUCLID,
                "Dot": models.Distance.DOT,
            }
            
            distance_metric = distance_map.get(distance, models.Distance.COSINE)
            
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=distance_metric,
                ),
            )
            
            logger.info(f"Created collection '{name}' with vector size {vector_size}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            return False
    
    def get_collection_info(self, collection_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get collection information.
        
        Args:
            collection_name: Collection name (defaults to configured collection)
            
        Returns:
            Collection info dictionary or None if error
        """
        name = collection_name or self.collection_name
        
        try:
            info = self.client.get_collection(collection_name=name)
            collection_info: Dict[str, Any] = {
                "name": name,
                "status": info.status,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "config": {}
            }
            
            ***REMOVED*** Safe attribute access with proper checking
            if hasattr(info, "config") and info.config is not None:
                config = info.config
                if hasattr(config, "params") and config.params is not None:
                    params = config.params
                    if hasattr(params, "vectors") and params.vectors is not None:
                        vectors = params.vectors
                        ***REMOVED*** Safely extract vector size if present
                        if isinstance(vectors, dict) and "size" in vectors:
                            collection_info["config"]["vector_size"] = vectors["size"]
                        elif hasattr(vectors, "size"):
                            collection_info["config"]["vector_size"] = vectors.size
                            
                        ***REMOVED*** Safely extract distance if present
                        if isinstance(vectors, dict) and "distance" in vectors:
                            if hasattr(vectors["distance"], "value"):
                                collection_info["config"]["distance"] = vectors["distance"].value
                        elif hasattr(vectors, "distance") and vectors.distance is not None:
                            if hasattr(vectors.distance, "value"):
                                collection_info["config"]["distance"] = vectors.distance.value
            
            return collection_info
        except Exception as e:
            logger.error(f"Error getting collection info for '{name}': {e}")
            return None
    
    def upsert_points(
        self,
        points: List[models.PointStruct],
        collection_name: Optional[str] = None,
    ) -> bool:
        """Upsert points into collection.
        
        Args:
            points: List of points to upsert
            collection_name: Collection name (defaults to configured collection)
            
        Returns:
            True if successful, False otherwise
        """
        name = collection_name or self.collection_name
        
        try:
            self.client.upsert(
                collection_name=name,
                points=points,
            )
            logger.info(f"Upserted {len(points)} points to collection '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting points to '{name}': {e}")
            return False
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        collection_name: Optional[str] = None,
        query_filter: Optional[models.Filter] = None,
    ) -> List[models.ScoredPoint]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            collection_name: Collection name (defaults to configured collection)
            query_filter: Optional filter for search
            
        Returns:
            List of scored points
        """
        name = collection_name or self.collection_name
        
        try:
            results = self.client.search(
                collection_name=name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )
            
            logger.info(f"Found {len(results)} similar vectors in collection '{name}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching in collection '{name}': {e}")
            return []
    
    def get_point(
        self,
        point_id: int,
        collection_name: Optional[str] = None,
        with_vectors: bool = True,
    ) -> Optional[models.Record]:
        """Get a specific point by ID.
        
        Args:
            point_id: Point ID
            collection_name: Collection name (defaults to configured collection)
            with_vectors: Whether to include vectors in the result
            
        Returns:
            Point record or None if not found
        """
        name = collection_name or self.collection_name
        
        try:
            ***REMOVED*** Explicitly request vectors to be included
            result = self.client.retrieve(
                collection_name=name,
                ids=[point_id],
                with_vectors=with_vectors,
            )
            
            logger.debug(f"Retrieved point {point_id} with with_vectors={with_vectors}")
            if result and len(result) > 0:
                if hasattr(result[0], 'vector'):
                    logger.debug(f"Point has vector attribute: {result[0].vector is not None}")
                
                return result[0]
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving point {point_id} from '{name}': {e}")
            return None
    
    def delete_points(
        self,
        point_ids: List[int],
        collection_name: Optional[str] = None,
    ) -> bool:
        """Delete points by IDs.
        
        Args:
            point_ids: List of point IDs to delete
            collection_name: Collection name (defaults to configured collection)
            
        Returns:
            True if successful, False otherwise
        """
        name = collection_name or self.collection_name
        
        try:
            ***REMOVED*** Convert to the appropriate type for Qdrant API
            ***REMOVED*** The API expects List[Union[int, str]], but we'll use all strings for consistency
            point_ids_for_api: List[Union[int, str]] = [str(point_id) for point_id in point_ids]
            
            self.client.delete(
                collection_name=name,
                points_selector=models.PointIdsList(
                    points=point_ids_for_api,
                ),
            )
            
            logger.info(f"Deleted {len(point_ids)} points from collection '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting points from '{name}': {e}")
            return False


def get_qdrant_client() -> "QdrantClient":
    """Get the global Qdrant client instance.
    
    Returns:
        QdrantClient instance
    """
    global _qdrant_client
    
    if _qdrant_client is None:
        logger.info("Creating Qdrant client")
        
        ***REMOVED*** Create base client
        base_client = QdrantClientBase(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )
        
        ***REMOVED*** Wrap in our client and assign to global variable
        wrapper_client = QdrantClient(base_client)
        _qdrant_client = wrapper_client
        
        ***REMOVED*** Test connection
        if not wrapper_client.test_connection():
            logger.warning("Qdrant connection test failed")
        
        logger.info("Qdrant client created successfully")
    
    ***REMOVED*** We've ensured _qdrant_client is not None at this point
    assert _qdrant_client is not None
    return _qdrant_client


def close_qdrant_client() -> None:
    """Close the global Qdrant client (useful for testing)."""
    global _qdrant_client
    if _qdrant_client is not None:
        ***REMOVED*** Access the underlying client through our wrapper class
        if hasattr(_qdrant_client, "client"):
            _qdrant_client.client.close()
        _qdrant_client = None
        logger.info("Qdrant client closed") 