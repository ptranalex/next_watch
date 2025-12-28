"""Credit model definition."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from movie_storage.models.movie import Movie


class Credit(SQLModel, table=True):
    """Credit model representing a cast or crew member for a movie."""

    id: int | None = Field(default=None, primary_key=True)

    ***REMOVED*** Foreign key to Movie
    movie_id: int | None = Field(default=None, foreign_key="movie.id")

    ***REMOVED*** Person information
    tmdb_person_id: int = Field(index=True)
    name: str
    original_name: str | None = None
    character: str | None = None

    ***REMOVED*** Department and role information
    department: str | None = None
    job: str | None = None

    ***REMOVED*** Cast specific information
    cast_id: int | None = None
    order: int | None = None

    ***REMOVED*** Person details
    gender: int | None = None
    profile_path: str | None = None
    popularity: float | None = None

    ***REMOVED*** Metadata
    credit_id: str | None = None
    adult: bool | None = False

    ***REMOVED*** Relationship back to Movie
    movie: Optional["Movie"] = Relationship(back_populates="credits")
