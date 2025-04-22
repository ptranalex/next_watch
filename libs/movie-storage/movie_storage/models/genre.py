"""Genre model definition."""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from movie_storage.models.movie import Movie, MovieGenreLink


class Genre(SQLModel, table=True):
    """Genre model representing a movie category/genre."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tmdb_id: Optional[int] = Field(default=None, index=True, unique=True)

    ***REMOVED*** Relationships
    movies: List["Movie"] = Relationship(
        back_populates="genres", link_model="movie_storage.models.movie.MovieGenreLink"
    )
