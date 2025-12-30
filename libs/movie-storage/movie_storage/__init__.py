"""Movie storage operations module."""

from movie_storage.cli import app as cli_app

# Export database utilities
from movie_storage.db import get_engine, get_session, init_db

# Export migrations
from movie_storage.db.migrations import run_migration

# Export database operations
from movie_storage.db.operations import (
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

# Export models
from movie_storage.models import Credit, Genre, Movie, MovieGenreLink

# Export other utilities
from movie_storage.utils import setup_movie_storage

# Package version
__version__ = "0.1.0"

# Define all exported names
__all__: list[str] = [
    # Models
    "Movie",
    "Genre",
    "MovieGenreLink",
    "Credit",
    # Database operations - Movies
    "create_movie",
    "get_movie_by_tmdb_id",
    "get_movie_by_id",
    "get_movie_by_imdb_id",
    "get_movies",
    "update_movie",
    "delete_movie",
    # Database operations - Genres
    "create_genre",
    "get_genre_by_id",
    "get_genre_by_name",
    "get_genre_by_tmdb_id",
    "get_genres",
    "update_genre",
    "delete_genre",
    # Database utilities
    "get_engine",
    "get_session",
    "init_db",
    # Migration utilities
    "run_migration",
    # Other utilities
    "setup_movie_storage",
    # CLI app
    "cli_app",
]
