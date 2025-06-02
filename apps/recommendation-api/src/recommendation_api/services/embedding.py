"""Embedding service for text embedding generation.

This module provides functions for generating embeddings from movie features
and user preferences using SentenceTransformers.
"""

import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
***REMOVED*** Type ignore for missing library stubs
from sentence_transformers import SentenceTransformer  ***REMOVED*** type: ignore

from recommendation_api.config import settings

logger = logging.getLogger(__name__)

***REMOVED*** Global model instance
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Get the global embedding model instance.
    
    Returns:
        SentenceTransformer model
    """
    global _model
    
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        logger.info(f"Embedding model loaded with dimension: {_model.get_sentence_embedding_dimension()}")
    
    return _model


def generate_movie_embedding(features: Dict[str, Any]) -> List[float]:
    """Generate an embedding for a movie based on its features.
    
    Args:
        features: Dictionary of movie features
        
    Returns:
        Embedding vector as list of floats
    """
    ***REMOVED*** Create text representation of movie
    text_parts = []
    
    if title := features.get("title"):
        text_parts.append(f"Title: {title}")
    
    if overview := features.get("overview"):
        ***REMOVED*** Truncate overview to avoid token limits
        overview_truncated = overview[:500] if len(overview) > 500 else overview
        text_parts.append(f"Plot: {overview_truncated}")
    
    if genres := features.get("genres"):
        if isinstance(genres, list) and genres:
            genres_str = ", ".join(genres)
            text_parts.append(f"Genres: {genres_str}")
    
    if cast := features.get("cast"):
        if isinstance(cast, list) and cast:
            ***REMOVED*** Use top 3 cast members
            cast_str = ", ".join(cast[:3])
            text_parts.append(f"Starring: {cast_str}")
    
    if director := features.get("director"):
        text_parts.append(f"Directed by: {director}")
    
    if release_year := features.get("release_year"):
        text_parts.append(f"Released: {release_year}")
    
    ***REMOVED*** Join all parts with periods
    movie_text = ". ".join(text_parts)
    
    ***REMOVED*** Get embedding
    model = get_embedding_model()
    embedding = model.encode(movie_text)
    
    ***REMOVED*** Convert to list of floats
    return embedding.tolist()


def generate_user_preference_vector(texts: List[str]) -> List[float]:
    """Generate a user preference vector from multiple movie texts.
    
    This creates embeddings for each text and then averages them to create
    a single vector representing the user's preferences.
    
    Args:
        texts: List of text representations of movies
        
    Returns:
        User preference vector as list of floats
    """
    if not texts:
        raise ValueError("No texts provided for user preference embedding")
    
    ***REMOVED*** Get embedding model
    model = get_embedding_model()
    
    ***REMOVED*** Generate embeddings for each text
    embeddings = model.encode(texts)
    
    ***REMOVED*** Average embeddings
    avg_embedding = np.mean(embeddings, axis=0)
    
    ***REMOVED*** Convert to list of floats
    return avg_embedding.tolist() 