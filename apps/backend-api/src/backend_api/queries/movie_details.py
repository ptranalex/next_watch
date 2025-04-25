"""
Query implementations for retrieving detailed information about movies.
"""

from sqlalchemy.sql import text
from typing import List, Dict, Any, Optional
import logging

from backend_api.queries.common import DBSession

logger = logging.getLogger(__name__)


def get_movie_genres(
    db_session: DBSession, movie_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all genres for a specific movie.

    Args:
        db_session: SQLAlchemy database session
        movie_id: The ID of the movie, or None to return an empty list

    Returns:
        List of genre rows, or empty list if movie_id is None
    """
    if movie_id is None:
        return []  ***REMOVED*** Return empty list if movie_id is None

    query = """
    SELECT g.*
    FROM genre g
    JOIN movie_genre_link mgl ON g.id = mgl.genre_id
    WHERE mgl.movie_id = :movie_id
    """

    result = db_session.execute(text(query), {"movie_id": int(movie_id)})
    return [
        dict(row._mapping) for row in result.all()
    ]  ***REMOVED*** Convert Row objects to dictionaries


def get_movie_details_by_id(
    db_session: DBSession, movie_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific movie by its ID.

    Args:
        db_session: SQLAlchemy database session
        movie_id: Movie ID

    Returns:
        Movie details dictionary or None if not found
    """
    query = """
    SELECT m.*
    FROM movie m
    WHERE m.id = :movie_id
    """

    result = db_session.execute(text(query), {"movie_id": movie_id})
    movie = result.first()

    if not movie:
        return None

    ***REMOVED*** Convert to dictionary
    return dict(movie._mapping)


def get_movie_details_by_tmdb_id(
    db_session: DBSession, tmdb_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific movie by its TMDB ID.

    Args:
        db_session: SQLAlchemy database session
        tmdb_id: TMDB ID

    Returns:
        Movie details dictionary or None if not found
    """
    query = """
    SELECT m.*
    FROM movie m
    WHERE m.tmdb_id = :tmdb_id
    """

    result = db_session.execute(text(query), {"tmdb_id": tmdb_id})
    movie = result.first()

    if not movie:
        return None

    ***REMOVED*** Convert to dictionary
    return dict(movie._mapping)
