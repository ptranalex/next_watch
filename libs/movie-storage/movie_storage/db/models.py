from typing import Optional, List
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship


class MovieGenreLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(
        default=None, foreign_key="movie.id", primary_key=True
    )
    genre_id: Optional[int] = Field(
        default=None, foreign_key="genre.id", primary_key=True
    )


class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    tmdb_id: int = Field(index=True, unique=True)
    imdb_id: Optional[str] = Field(default=None, index=True)

    title: str
    original_title: Optional[str]
    overview: Optional[str]
    language: Optional[str]

    release_date: Optional[date]
    runtime: Optional[int]

    poster_url: Optional[str]
    backdrop_url: Optional[str]

    tmdb_rating: Optional[float]
    imdb_rating: Optional[float]
    popularity: Optional[float]
    budget: Optional[int]
    revenue: Optional[int]

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    genres: List["Genre"] = Relationship(
        back_populates="movies", link_model=MovieGenreLink
    )


class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tmdb_id: Optional[int] = Field(default=None, index=True, unique=True)

    movies: List[Movie] = Relationship(
        back_populates="genres", link_model=MovieGenreLink
    )
