"""Database operations package for the Recommendation API service."""

***REMOVED*** Import from movie_storage.db
from movie_storage.db import get_engine

***REMOVED*** Import from local connection.py
from .connection import get_db_session, get_db_context, init_database, test_connection, get_simple_session

***REMOVED*** Import from operations.py
from .operations import (
    get_movies_for_embeddings,
    get_movie_features,
    get_movies_by_ids,
    get_movie_by_id,
)

__all__ = [
    ***REMOVED*** Database connection
    "get_db_session",
    "get_db_context",
    "init_database",
    "test_connection",
    "get_engine",  ***REMOVED*** This replaces get_db_engine
    "get_simple_session",
    
    ***REMOVED*** Database operations
    "get_movies_for_embeddings",
    "get_movie_features",
    "get_movies_by_ids",
    "get_movie_by_id",
] 