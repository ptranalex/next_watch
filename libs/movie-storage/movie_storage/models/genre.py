"""Genre model definition."""

from typing import Optional, List, TYPE_CHECKING, ForwardRef
from sqlmodel import SQLModel, Field, Relationship

***REMOVED*** Import the MovieGenreLink class directly instead of using TYPE_CHECKING
from movie_storage.models.movie import MovieGenreLink

if TYPE_CHECKING:
    from movie_storage.models.movie import Movie


class Genre(SQLModel, table=True):
    """Genre model representing a movie category/genre."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tmdb_id: Optional[int] = Field(default=None, index=True, unique=True)

    ***REMOVED*** Relationships
    movies: List["Movie"] = Relationship(
        back_populates="genres", link_model=MovieGenreLink
    )
