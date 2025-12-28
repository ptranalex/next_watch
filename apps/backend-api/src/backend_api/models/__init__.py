"""Model definitions for the movie storage library."""

from backend_api.models.credit import Credit
from backend_api.models.genre import Genre

***REMOVED*** Re-export all models from their respective modules
from backend_api.models.movie import Movie, MovieGenreLink
from backend_api.models.trailer import Trailer
from backend_api.models.user import User
from backend_api.models.user_interaction import UserMovieInteraction

__all__: list[str] = [
    "Movie",
    "MovieGenreLink",
    "Genre",
    "Credit",
    "Trailer",
    "User",
    "UserMovieInteraction",
]
