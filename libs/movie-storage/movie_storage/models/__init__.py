"""Model definitions for the movie storage library."""

from typing import List

from movie_storage.models.credit import Credit
from movie_storage.models.genre import Genre

***REMOVED*** Re-export all models from their respective modules
from movie_storage.models.movie import Movie, MovieGenreLink
from movie_storage.models.trailer import Trailer
from movie_storage.models.user import User
from movie_storage.models.user_interaction import UserMovieInteraction

__all__: List[str] = [
    "Movie",
    "MovieGenreLink",
    "Genre",
    "Credit",
    "Trailer",
    "User",
    "UserMovieInteraction",
]
