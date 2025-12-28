"""Movie model definition."""

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend_api.models.credit import Credit
    from backend_api.models.genre import Genre
    from backend_api.models.trailer import Trailer
    from backend_api.models.user_interaction import UserMovieInteraction


class MovieGenreLink(SQLModel, table=True):
    """Association table for Movie-Genre many-to-many relationship."""

    __tablename__ = "movie_genre_link"  ***REMOVED*** pyright: ignore

    movie_id: int | None = Field(default=None, foreign_key="movie.id", primary_key=True)
    genre_id: int | None = Field(default=None, foreign_key="genre.id", primary_key=True)


class Movie(SQLModel, table=True):
    """Movie model representing a film in the database."""

    id: int | None = Field(default=None, primary_key=True)

    ***REMOVED*** IDs from external sources
    tmdb_id: int = Field(index=True, unique=True)
    imdb_id: str | None = Field(default=None, index=True)

    ***REMOVED*** Basic information
    title: str
    original_title: str | None
    overview: str | None
    tagline: str | None = None
    status: str | None = None

    ***REMOVED*** Language and country information
    language: str | None
    original_language: str | None = None
    origin_country: str | None = None

    ***REMOVED*** Collection information
    belongs_to_collection_id: int | None = None
    belongs_to_collection_name: str | None = None

    ***REMOVED*** Release and runtime information
    release_date: date | None
    runtime: int | None

    ***REMOVED*** URLs and paths
    poster_url: str | None
    backdrop_url: str | None
    homepage: str | None = None

    ***REMOVED*** Performance metrics
    popularity: float | None
    vote_average: float | None = None
    vote_count: int | None = None

    ***REMOVED*** Financial information (using BIGINT for large values)
    budget: int | None = Field(sa_column=Column(BigInteger), default=None)
    revenue: int | None = Field(sa_column=Column(BigInteger), default=None)

    ***REMOVED*** Boolean flags
    adult: bool | None = False
    video: bool | None = False

    ***REMOVED*** Ratings from different sources
    tmdb_rating: float | None
    imdb_rating: float | None
    rotten_tomatoes_rating: int | None = None
    metacritic_rating: int | None = None

    ***REMOVED*** Awards information
    awards: str | None = None

    ***REMOVED*** Timestamp fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    ***REMOVED*** Relationships
    genres: list["Genre"] = Relationship(
        back_populates="movies", link_model=MovieGenreLink
    )
    credits: list["Credit"] = Relationship(back_populates="movie")
    trailers: list["Trailer"] = Relationship(back_populates="movie")
    user_interactions: list["UserMovieInteraction"] = Relationship(
        back_populates="movie"
    )
