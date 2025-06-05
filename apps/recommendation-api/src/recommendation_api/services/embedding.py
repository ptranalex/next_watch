"""Embedding service for text embedding generation (DEPRECATED).

This module previously provided functions for generating embeddings from movie features
and user preferences using SentenceTransformers. It has been replaced by the ML API client.

DO NOT USE DIRECTLY - All ML computation has been offloaded to the ML API service.
"""

import logging
from typing import List, Dict, Any, Optional, Union
import warnings

from recommendation_api.services.ml_api_client import get_ml_api_client

logger = logging.getLogger(__name__)

***REMOVED*** Show deprecation warning when this module is imported
warnings.warn(
    "The local embedding service is deprecated. ML computation has been "
    "offloaded to the ML API service. Use ml_api_client instead.",
    DeprecationWarning,
    stacklevel=2
)


async def generate_movie_embedding(features: Dict[str, Any]) -> List[float]:
    """Generate an embedding for a movie based on its features.
    
    DEPRECATED: This function now redirects to the ML API client.
    
    Args:
        features: Dictionary of movie features
        
    Returns:
        Embedding vector as list of floats
    """
    warnings.warn(
        "Using local generate_movie_embedding is deprecated. Use ML API client instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    logger.warning("Redirecting generate_movie_embedding call to ML API client")
    client = get_ml_api_client()
    return await client.generate_movie_embedding(features)


async def generate_user_preference_vector(texts: List[str]) -> List[float]:
    """Generate a user preference vector from multiple movie texts.
    
    DEPRECATED: This function now redirects to the ML API client.
    
    Args:
        texts: List of text representations of movies
        
    Returns:
        User preference vector as list of floats
    """
    warnings.warn(
        "Using local generate_user_preference_vector is deprecated. Use ML API client instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    logger.warning("Redirecting generate_user_preference_vector call to ML API client")
    client = get_ml_api_client()
    
    ***REMOVED*** The ML API expects a different format - this is just a compatibility layer
    ***REMOVED*** In a real implementation, you might want to convert the texts to the format expected by the ML API
    mock_features = {
        "title": "User Preferences",
        "overview": " ".join(texts[:3]),  ***REMOVED*** Use first few texts as a summary
        "genres": [],
    }
    
    return await client.generate_movie_embedding(mock_features) 