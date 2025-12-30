"""Genre model definition."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# Import the MovieGenreLink class directly instead of using TYPE_CHECKING
from movie_storage.models.movie import MovieGenreLink

if TYPE_CHECKING:
    from movie_storage.models.movie import Movie


class Genre(SQLModel, table=True):
    """Genre model representing a movie category/genre."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    tmdb_id: int | None = Field(default=None, index=True, unique=True)

    # Relationships
    movies: list["Movie"] = Relationship(back_populates="genres", link_model=MovieGenreLink)
