"""Trailer model definition."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend_api.models.movie import Movie


class Trailer(SQLModel, table=True):
    """Trailer model representing a movie trailer or video."""

    id: int | None = Field(default=None, primary_key=True)

    ***REMOVED*** Foreign key to Movie
    movie_id: int = Field(foreign_key="movie.id")

    ***REMOVED*** Trailer information
    youtube_key: str = Field(index=True)
    name: str
    is_official: bool = Field(default=True)
    url_link: str | None = None

    ***REMOVED*** Timestamp fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    ***REMOVED*** Relationship back to Movie
    movie: Optional["Movie"] = Relationship(back_populates="trailers")
