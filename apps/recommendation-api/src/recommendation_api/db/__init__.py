"""Database operations package for the Recommendation API service."""

from .connection import get_db_session, get_db_engine
from .operations import (
    get_movies_for_embeddings,
    get_user_movie_interactions,
    get_movie_features,
    create_movie_similarity,
    get_movie_similarities,
    get_trending_movies,
    get_popular_movies,
)

__all__ = [
    "get_db_session",
    "get_db_engine", 
    "get_movies_for_embeddings",
    "get_user_movie_interactions",
    "get_movie_features",
    "create_movie_similarity",
    "get_movie_similarities",
    "get_trending_movies",
    "get_popular_movies",
] 