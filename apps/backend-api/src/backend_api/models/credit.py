"""Credit model definition."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend_api.models.movie import Movie


class Credit(SQLModel, table=True):
    """Credit model representing a cast or crew member for a movie."""

    id: Optional[int] = Field(default=None, primary_key=True)

    ***REMOVED*** Foreign key to Movie
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id")

    ***REMOVED*** Person information
    tmdb_person_id: int = Field(index=True)
    name: str
    original_name: Optional[str] = None
    character: Optional[str] = None

    ***REMOVED*** Department and role information
    department: Optional[str] = None
    job: Optional[str] = None

    ***REMOVED*** Cast specific information
    cast_id: Optional[int] = None
    order: Optional[int] = None

    ***REMOVED*** Person details
    gender: Optional[int] = None
    profile_path: Optional[str] = None
    popularity: Optional[float] = None

    ***REMOVED*** Metadata
    credit_id: Optional[str] = None
    adult: Optional[bool] = False

    ***REMOVED*** Relationship back to Movie
    movie: Optional["Movie"] = Relationship(back_populates="credits")
