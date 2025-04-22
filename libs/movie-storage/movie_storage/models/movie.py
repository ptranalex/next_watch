"""Movie model definition."""

from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from movie_storage.models.genre import Genre
    from movie_storage.models.credit import Credit


class MovieGenreLink(SQLModel, table=True):
    """Association table for Movie-Genre many-to-many relationship."""

    movie_id: Optional[int] = Field(
        default=None, foreign_key="movie.id", primary_key=True
    )
    genre_id: Optional[int] = Field(
        default=None, foreign_key="genre.id", primary_key=True
    )


class Movie(SQLModel, table=True):
    """Movie model representing a film in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)

    ***REMOVED*** IDs from external sources
    tmdb_id: int = Field(index=True, unique=True)
    imdb_id: Optional[str] = Field(default=None, index=True)

    ***REMOVED*** Basic information
    title: str
    original_title: Optional[str]
    overview: Optional[str]
    tagline: Optional[str] = None
    status: Optional[str] = None

    ***REMOVED*** Language and country information
    language: Optional[str]
    original_language: Optional[str] = None
    origin_country: Optional[str] = None

    ***REMOVED*** Collection information
    belongs_to_collection_id: Optional[int] = None
    belongs_to_collection_name: Optional[str] = None

    ***REMOVED*** Release and runtime information
    release_date: Optional[date]
    runtime: Optional[int]

    ***REMOVED*** URLs and paths
    poster_url: Optional[str]
    backdrop_url: Optional[str]
    homepage: Optional[str] = None

    ***REMOVED*** Performance metrics
    popularity: Optional[float]
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None

    ***REMOVED*** Financial information
    budget: Optional[int]
    revenue: Optional[int]

    ***REMOVED*** Boolean flags
    adult: Optional[bool] = False
    video: Optional[bool] = False

    ***REMOVED*** Legacy ratings (may be kept for compatibility)
    tmdb_rating: Optional[float]
    imdb_rating: Optional[float]

    ***REMOVED*** Timestamp fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    ***REMOVED*** Relationships
    genres: List["Genre"] = Relationship(
        back_populates="movies", link_model=MovieGenreLink
    )
    credits: List["Credit"] = Relationship(back_populates="movie")
