"""Database operations module."""

***REMOVED*** Import repositories and operations
from movie_storage.db.operations.movie import (
    create_movie,
    get_movie_by_tmdb_id,
    get_movie_by_id,
    get_movie_by_imdb_id,
    get_movies,
    update_movie,
    delete_movie,
)

from movie_storage.db.operations.genre import (
    create_genre,
    get_genre_by_id,
    get_genre_by_name,
    get_genre_by_tmdb_id,
    get_genres,
    update_genre,
    delete_genre,
)

__all__ = [
    "create_movie",
    "get_movie_by_tmdb_id",
    "get_movie_by_id",
    "get_movie_by_imdb_id",
    "get_movies",
    "update_movie",
    "delete_movie",
    "create_genre",
    "get_genre_by_id",
    "get_genre_by_name",
    "get_genre_by_tmdb_id",
    "get_genres",
    "update_genre",
    "delete_genre",
]
