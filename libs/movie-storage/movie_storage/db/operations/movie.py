"""Movie storage operations."""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

from sqlmodel import Session, select, or_
from sqlalchemy.sql import text
from sqlalchemy import func

from movie_storage.db.models import Movie, Genre, MovieGenreLink

logger = logging.getLogger(__name__)


def create_movie(
    session: Session, movie_data: Dict[str, Any], genre_ids: Optional[List[int]] = None
) -> Movie:
    """Create a movie record and associate it with genres.

    Args:
        session: Database session
        movie_data: Movie data dictionary
        genre_ids: List of genre IDs to associate with the movie

    Returns:
        Created Movie instance
    """
    ***REMOVED*** Create a copy to avoid modifying the input
    movie_dict = movie_data.copy()

    ***REMOVED*** Extract genre information if present to prevent SQLModel errors
    if "genres" in movie_dict:
        del movie_dict["genres"]

    ***REMOVED*** Create movie instance
    movie = Movie(**movie_dict)
    session.add(movie)
    session.flush()  ***REMOVED*** Flush to get the generated ID

    ***REMOVED*** Associate genres if provided
    if genre_ids:
        for genre_id in genre_ids:
            link = MovieGenreLink(movie_id=movie.id, genre_id=genre_id)
            session.add(link)

    session.commit()
    session.refresh(movie)
    return movie


def get_movie_by_id(session: Session, movie_id: int) -> Optional[Movie]:
    """Get a movie by its primary key ID.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        Movie instance or None if not found
    """
    return session.get(Movie, movie_id)


def get_movie_by_tmdb_id(session: Session, tmdb_id: int) -> Optional[Movie]:
    """Get a movie by its TMDB ID.

    Args:
        session: Database session
        tmdb_id: TMDB ID

    Returns:
        Movie instance or None if not found
    """
    statement = select(Movie).where(Movie.tmdb_id == tmdb_id)
    result = session.exec(statement).first()
    return result


def get_movie_by_imdb_id(session: Session, imdb_id: str) -> Optional[Movie]:
    """Get a movie by its IMDB ID.

    Args:
        session: Database session
        imdb_id: IMDB ID

    Returns:
        Movie instance or None if not found
    """
    statement = select(Movie).where(Movie.imdb_id == imdb_id)
    result = session.exec(statement).first()
    return result


def get_movies(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    title_search: Optional[str] = None,
    genre_id: Optional[int] = None,
    sort_by: str = "title",
    sort_desc: bool = False,
) -> List[Movie]:
    """Get movies with optional filtering and sorting.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        title_search: Optional title search string
        genre_id: Optional genre ID to filter by
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order

    Returns:
        List of Movie instances
    """
    query = select(Movie)

    ***REMOVED*** Apply title search if provided
    if title_search:
        search_pattern = f"%{title_search}%"
        query = query.where(func.lower(Movie.title).like(func.lower(search_pattern)))

    ***REMOVED*** Apply genre filter if provided
    if genre_id:
        query = query.join(MovieGenreLink).where(MovieGenreLink.genre_id == genre_id)

    ***REMOVED*** Apply sorting
    if hasattr(Movie, sort_by):
        sort_field = getattr(Movie, sort_by)
        if sort_desc:
            sort_field = sort_field.desc()
        query = query.order_by(sort_field)

    ***REMOVED*** Apply pagination
    movies = session.exec(query.offset(skip).limit(limit)).all()
    return list(movies)


def update_movie(
    session: Session,
    movie_id: int,
    movie_data: Dict[str, Any],
    genre_ids: Optional[List[int]] = None,
) -> Optional[Movie]:
    """Update a movie record.

    Args:
        session: Database session
        movie_id: ID of the movie to update
        movie_data: Updated movie data
        genre_ids: List of genre IDs to associate with the movie

    Returns:
        Updated Movie instance or None if not found
    """
    movie = get_movie_by_id(session, movie_id)

    if not movie:
        return None

    ***REMOVED*** Create a copy to avoid modifying the input
    movie_dict = movie_data.copy()

    ***REMOVED*** Extract genre information if present
    if "genres" in movie_dict:
        del movie_dict["genres"]

    ***REMOVED*** Update movie attributes
    for key, value in movie_dict.items():
        if hasattr(movie, key):
            setattr(movie, key, value)

    ***REMOVED*** Set updated_at timestamp
    movie.updated_at = datetime.utcnow()

    ***REMOVED*** Update genre associations if provided
    if genre_ids is not None:
        ***REMOVED*** Remove existing genre links
        links = session.exec(
            select(MovieGenreLink).where(MovieGenreLink.movie_id == movie_id)
        ).all()
        for link in links:
            session.delete(link)

        ***REMOVED*** Add new genre links
        for genre_id in genre_ids:
            link = MovieGenreLink(movie_id=movie_id, genre_id=genre_id)
            session.add(link)

    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


def delete_movie(session: Session, movie_id: int) -> bool:
    """Delete a movie record.

    Args:
        session: Database session
        movie_id: ID of the movie to delete

    Returns:
        True if deleted, False if not found
    """
    movie = get_movie_by_id(session, movie_id)

    if not movie:
        return False

    ***REMOVED*** Remove genre links
    links = session.exec(
        select(MovieGenreLink).where(MovieGenreLink.movie_id == movie_id)
    ).all()
    for link in links:
        session.delete(link)

    ***REMOVED*** Delete movie
    session.delete(movie)
    session.commit()
    return True
