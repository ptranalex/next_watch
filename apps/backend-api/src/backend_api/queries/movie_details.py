"""
Query implementations for retrieving detailed information about movies.
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.sql import text

from backend_api.queries.common import DBSession

logger = logging.getLogger(__name__)


def get_movie_genres(db_session: DBSession, movie_id: Optional[int] = None) -> List[Dict[str, Any]]:
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
    return [dict(row._mapping) for row in result.all()]  ***REMOVED*** Convert Row objects to dictionaries


def get_movie_details_by_id(db_session: DBSession, movie_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific movie by its ID.

    Args:
        db_session: SQLAlchemy database session
        movie_id: Movie ID

    Returns:
        Movie details dictionary or None if not found
    """
    ***REMOVED*** Get movie details with director, writer, and ratings
    movie_query = """
    SELECT m.*, 
           (SELECT c.name 
            FROM credit c 
            WHERE c.movie_id = m.id 
            AND c.department = 'Directing' 
            AND c.job = 'Director' 
            LIMIT 1) as director,
           (SELECT c.name 
            FROM credit c 
            WHERE c.movie_id = m.id 
            AND c.department = 'Writing' 
            AND c.job = 'Screenplay' 
            LIMIT 1) as writer
    FROM movie m
    WHERE m.id = :movie_id
    """

    result = db_session.execute(text(movie_query), {"movie_id": movie_id})
    movie = result.first()

    if not movie:
        return None

    ***REMOVED*** Get credits
    credits_query = """
    SELECT c.*
    FROM credit c
    WHERE c.movie_id = :movie_id
    """

    credits_result = db_session.execute(text(credits_query), {"movie_id": movie_id})
    credits = [dict(row._mapping) for row in credits_result.all()]

    ***REMOVED*** Combine movie and credits
    movie_dict = dict(movie._mapping)
    movie_dict["credits"] = credits

    return movie_dict


def get_movie_details_by_tmdb_id(db_session: DBSession, tmdb_id: int) -> Optional[Dict[str, Any]]:
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


def get_movies_by_ids_bulk(db_session: DBSession, movie_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Get detailed information about multiple movies by their IDs.

    Args:
        db_session: SQLAlchemy database session
        movie_ids: List of movie IDs to fetch

    Returns:
        List of movie details dictionaries
    """
    if not movie_ids:
        return []

    ***REMOVED*** Create placeholders for the IN clause
    placeholders = ",".join([":id" + str(i) for i in range(len(movie_ids))])

    ***REMOVED*** Build the query with proper parameter substitution
    query = f"""
    SELECT m.*, 
           (SELECT c.name 
            FROM credit c 
            WHERE c.movie_id = m.id 
            AND c.department = 'Directing' 
            AND c.job = 'Director' 
            LIMIT 1) as director,
           (SELECT c.name 
            FROM credit c 
            WHERE c.movie_id = m.id 
            AND c.department = 'Writing' 
            AND c.job = 'Screenplay' 
            LIMIT 1) as writer
    FROM movie m
    WHERE m.id IN ({placeholders})
    ORDER BY m.id
    """

    ***REMOVED*** Create parameters dictionary
    params = {f"id{i}": movie_id for i, movie_id in enumerate(movie_ids)}

    result = db_session.execute(text(query), params)
    movies = [dict(row._mapping) for row in result.all()]

    return movies
