"""Movie storage operations module."""

__version__ = "0.1.0"

***REMOVED*** Export models
from movie_storage.db.models import Movie, Genre, MovieGenreLink

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
from movie_storage.cli.main import main as cli_main
