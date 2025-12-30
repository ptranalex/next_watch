"""Trailer model definition."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from movie_storage.models.movie import Movie


class Trailer(SQLModel, table=True):
    """Trailer model representing a movie trailer or video."""

    id: int | None = Field(default=None, primary_key=True)

    # Foreign key to Movie
    movie_id: int = Field(foreign_key="movie.id")

    # Trailer information
    youtube_key: str = Field(index=True)
    name: str
    is_official: bool = Field(default=True)
    url_link: str | None = None

    # Timestamp fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship back to Movie
    movie: Optional["Movie"] = Relationship(back_populates="trailers")
