"""Movie storage operations module."""

from typing import List

__version__ = "0.1.0"

***REMOVED*** Export models
from movie_storage.models import Movie, Genre, MovieGenreLink, Credit

***REMOVED*** Export database operations
from movie_storage.db.operations import (
    create_movie,
    get_movie_by_tmdb_id,
    get_movie_by_id,
    get_movie_by_imdb_id,
    get_movies,
    update_movie,
    delete_movie,
    create_genre,
    get_genre_by_id,
    get_genre_by_name,
    get_genre_by_tmdb_id,
    get_genres,
    update_genre,
    delete_genre,
)

***REMOVED*** Export database utilities
from movie_storage.db import (
    get_engine,
    get_session,
    init_db,
)

***REMOVED*** Export migrations
from movie_storage.db.migrations import run_migration

***REMOVED*** Export other utilities
from movie_storage.utils import setup_movie_storage
from movie_storage.cli import app as cli_app

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
    "setup_movie_storage",
    ***REMOVED*** CLI app
    "cli_app",
]
