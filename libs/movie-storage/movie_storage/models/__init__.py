"""Models for the movie storage package."""

from typing import List

***REMOVED*** Re-export all models from their respective modules
from movie_storage.models.movie import Movie, MovieGenreLink
from movie_storage.models.genre import Genre
from movie_storage.models.credit import Credit

__all__: List[str] = [
    "Movie",
    "Genre",
    "MovieGenreLink",
    "Credit",
]
