"""Database operations module."""

***REMOVED*** Import repositories and operations
from movie_storage.db.operations.credit import (
    create_credit,
    create_credits_from_tmdb_data,
    delete_credit,
    delete_credits_for_movie,
    get_credit_by_id,
    get_credits,
    get_credits_by_movie_id,
    get_credits_by_person_id,
    update_credit,
)
from movie_storage.db.operations.genre import (
    create_genre,
    delete_genre,
    get_genre_by_id,
    get_genre_by_name,
    get_genre_by_tmdb_id,
    get_genres,
    update_genre,
)
from movie_storage.db.operations.movie import (
    create_movie,
    delete_movie,
    get_movie_by_id,
    get_movie_by_imdb_id,
    get_movie_by_tmdb_id,
    get_movies,
    update_movie,
)
from movie_storage.db.operations.trailer import create_trailer
from movie_storage.db.operations.user import (
    authenticate_user,
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    get_users,
    update_user,
)
from movie_storage.db.operations.user_interaction import (
    create_user_movie_interaction,
    delete_user_movie_interaction,
    get_user_liked_movies,
    get_user_movie_interaction,
    get_user_movie_interactions,
    get_user_watched_movies,
    get_user_watchlist,
    toggle_user_movie_interaction_flag,
    update_user_movie_interaction,
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
    ***REMOVED*** User operations
    "create_user",
    "get_user_by_id",
    "get_user_by_email",
    "get_user_by_username",
    "get_users",
    "update_user",
    "delete_user",
    "authenticate_user",
    ***REMOVED*** Trailer operations
    "create_trailer",
    ***REMOVED*** User interaction operations
    "create_user_movie_interaction",
    "get_user_movie_interaction",
    "get_user_movie_interactions",
    "get_user_watchlist",
    "get_user_watched_movies",
    "get_user_liked_movies",
    "update_user_movie_interaction",
    "delete_user_movie_interaction",
    "toggle_user_movie_interaction_flag",
]
