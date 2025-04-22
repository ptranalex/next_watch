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

from movie_storage.db.operations.credit import (
    create_credit,
    get_credit_by_id,
    get_credits_by_movie_id,
    get_credits_by_person_id,
    get_credits,
    update_credit,
    delete_credit,
    delete_credits_for_movie,
    create_credits_from_tmdb_data,
)

__all__ = [
    ***REMOVED*** Movie operations
    "create_movie",
    "get_movie_by_tmdb_id",
    "get_movie_by_id",
    "get_movie_by_imdb_id",
    "get_movies",
    "update_movie",
    "delete_movie",
    ***REMOVED*** Genre operations
    "create_genre",
    "get_genre_by_id",
    "get_genre_by_name",
    "get_genre_by_tmdb_id",
    "get_genres",
    "update_genre",
    "delete_genre",
    ***REMOVED*** Credit operations
    "create_credit",
    "get_credit_by_id",
    "get_credits_by_movie_id",
    "get_credits_by_person_id",
    "get_credits",
    "update_credit",
    "delete_credit",
    "delete_credits_for_movie",
    "create_credits_from_tmdb_data",
]
