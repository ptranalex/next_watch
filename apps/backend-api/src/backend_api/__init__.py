"""Movie storage operations module."""

from typing import List

__version__ = "0.1.0"

from backend_api.cli import app as cli_app

***REMOVED*** Export database utilities
from backend_api.db import get_engine, get_session, init_db

***REMOVED*** Export migrations
from backend_api.db.migrations import run_migration

***REMOVED*** Export database operations
from backend_api.db.operations import (
    create_genre,
    create_movie,
    delete_genre,
    delete_movie,
    get_genre_by_id,
    get_genre_by_name,
    get_genre_by_tmdb_id,
    get_genres,
    get_movie_by_id,
    get_movie_by_imdb_id,
    get_movie_by_tmdb_id,
    get_movies,
    update_genre,
    update_movie,
)

***REMOVED*** Export models
from backend_api.models import Credit, Genre, Movie, MovieGenreLink

***REMOVED*** Export other utilities
from backend_api.utils import setup_backend_api_storage

***REMOVED*** Define all exported names
__all__: List[str] = [
    ***REMOVED*** Models
    "Movie",
    "Genre",
    "MovieGenreLink",
    "Credit",
    ***REMOVED*** Database operations - Movies
    "create_movie",
    "get_movie_by_tmdb_id",
    "get_movie_by_id",
    "get_movie_by_imdb_id",
    "get_movies",
    "update_movie",
    "delete_movie",
    ***REMOVED*** Database operations - Genres
    "create_genre",
    "get_genre_by_id",
    "get_genre_by_name",
    "get_genre_by_tmdb_id",
    "get_genres",
    "update_genre",
    "delete_genre",
    ***REMOVED*** Database utilities
    "get_engine",
    "get_session",
    "init_db",
    ***REMOVED*** Migration utilities
    "run_migration",
    ***REMOVED*** Other utilities
    "setup_backend_api_storage",
    ***REMOVED*** CLI app
    "cli_app",
]
