"""
Movie query implementations for business logic operations.

This module contains specialized movie query implementations that are specific
to API business requirements, keeping them separate from the core data layer.
"""

from sqlalchemy.sql import text
from typing import List, Tuple, Dict, Any, Optional, Union, Sequence, cast, TypeVar
from datetime import datetime
import logging
from sqlalchemy.engine import Connection
from sqlmodel import Session

***REMOVED*** Define a type alias for database sessions that can be either Connection or Session
DBSession = TypeVar("DBSession", Session, Connection)

logger = logging.getLogger(__name__)


def get_top_rated_movies(
    db_session: DBSession,
    year: Optional[int] = None,
    all_time: bool = False,
    genre_name: Optional[str] = None,
    limit: int = 10,
    page: int = 1,
    min_votes: int = 100,
) -> Tuple[List[Any], int]:
    """
    Get top-rated movies by IMDB rating.

    Args:
        db_session: SQLAlchemy database session
        year: Optional year to filter movies by
        all_time: If True, gets all-time top movies regardless of year
        genre_name: Optional genre name to filter by
        limit: Maximum number of results to return
        page: Page number for pagination
        min_votes: Minimum number of votes required (for all_time queries)

    Returns:
        Tuple of (list of movie rows, total count)
    """
    ***REMOVED*** Default to current year if not all_time and no year specified
    if not all_time and year is None:
        year = datetime.now().year

    ***REMOVED*** Use raw SQL to avoid ORM complexities and typing issues
    query = """
    SELECT m.*, COUNT(g.id) as genre_count
    FROM movie m
    LEFT JOIN movie_genre_link mgl ON m.id = mgl.movie_id
    LEFT JOIN genre g ON mgl.genre_id = g.id
    WHERE m.imdb_rating IS NOT NULL
    """

    params: Dict[str, Union[str, int]] = {}

    ***REMOVED*** Apply year filter if not getting all-time movies
    if not all_time and year is not None:
        query += " AND EXTRACT(YEAR FROM m.release_date) = :year"
        params["year"] = int(year)

    ***REMOVED*** For all-time filter, apply minimum votes threshold
    if all_time:
        query += " AND m.vote_count IS NOT NULL AND m.vote_count >= :min_votes"
        params["min_votes"] = int(min_votes)

    ***REMOVED*** Apply genre filter if provided
    if genre_name:
        query += " AND LOWER(g.name) = LOWER(:genre_name)"
        params["genre_name"] = genre_name

    ***REMOVED*** Add group by
    query += " GROUP BY m.id"

    ***REMOVED*** Add ordering - prioritize IMDB rating, then vote count as tiebreaker
    query += " ORDER BY m.imdb_rating DESC NULLS LAST, m.vote_count DESC NULLS LAST"

    ***REMOVED*** Add pagination
    offset = (int(page) - 1) * int(limit)
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = int(limit)
    params["offset"] = int(offset)

    ***REMOVED*** Count query for pagination
    count_query = """
    SELECT COUNT(DISTINCT m.id) 
    FROM movie m
    LEFT JOIN movie_genre_link mgl ON m.id = mgl.movie_id
    LEFT JOIN genre g ON mgl.genre_id = g.id
    WHERE m.imdb_rating IS NOT NULL
    """

    ***REMOVED*** Apply the same filters to count query
    if not all_time and year is not None:
        count_query += " AND EXTRACT(YEAR FROM m.release_date) = :year"

    if all_time:
        count_query += " AND m.vote_count IS NOT NULL AND m.vote_count >= :min_votes"

    if genre_name:
        count_query += " AND LOWER(g.name) = LOWER(:genre_name)"

    ***REMOVED*** Execute queries
    result = db_session.execute(text(query), params)
    count_result = db_session.execute(text(count_query), params)

    movies = list(result.all())  ***REMOVED*** Convert to List
    total_count = count_result.scalar() or 0

    return movies, total_count


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


def get_movies_with_filters(
    db_session: DBSession,
    skip: int = 0,
    limit: int = 20,
    genre_id: Optional[int] = None,
    sort_by: str = "title",
    sort_desc: bool = False,
) -> Tuple[List[Any], int]:
    """
    Get movies with pagination, filtering, and sorting.

    Args:
        db_session: SQLAlchemy database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        genre_id: Optional genre ID to filter by
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order

    Returns:
        Tuple of (list of movie rows, total count)
    """
    ***REMOVED*** Base query
    query = """
    SELECT m.*
    FROM movie m
    """

    ***REMOVED*** If filtering by genre, join with genre table
    where_clauses = []
    params: Dict[str, Any] = {}

    if genre_id is not None:
        query += """
        JOIN movie_genre_link mgl ON m.id = mgl.movie_id 
        JOIN genre g ON mgl.genre_id = g.id
        """
        where_clauses.append("mgl.genre_id = :genre_id")
        params["genre_id"] = genre_id

    ***REMOVED*** Add WHERE clause if we have any conditions
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    ***REMOVED*** Add sorting
    valid_sort_fields = ["title", "release_date", "imdb_rating", "vote_count"]
    sort_field = sort_by if sort_by in valid_sort_fields else "title"

    query += f" ORDER BY m.{sort_field}"
    if sort_desc:
        query += " DESC"
    else:
        query += " ASC"

    ***REMOVED*** Add NULLS LAST for rating fields to ensure movies with ratings appear first
    if sort_field in ["imdb_rating", "vote_average", "vote_count"]:
        query += " NULLS LAST"

    ***REMOVED*** Add pagination
    query += " LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip

    ***REMOVED*** Count query
    if genre_id is not None:
        count_query = """
        SELECT COUNT(DISTINCT m.id) 
        FROM movie m
        JOIN movie_genre_link mgl ON m.id = mgl.movie_id
        WHERE mgl.genre_id = :genre_id
        """
    else:
        count_query = "SELECT COUNT(*) FROM movie"

    ***REMOVED*** Execute queries
    result = db_session.execute(text(query), params)
    count_result = db_session.execute(text(count_query), params)

    movies = list(result.all())
    total_count = count_result.scalar() or 0

    return movies, total_count


def search_movies_by_title(
    db_session: DBSession,
    title_search: str,
    skip: int = 0,
    limit: int = 20,
    genre_id: Optional[int] = None,
    sort_by: str = "title",
    sort_desc: bool = False,
) -> Tuple[List[Any], int]:
    """
    Search for movies by title with additional filtering options.

    Args:
        db_session: SQLAlchemy database session
        title_search: Title search string (case-insensitive partial match)
        skip: Number of records to skip
        limit: Maximum number of records to return
        genre_id: Optional genre ID to filter by
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order

    Returns:
        Tuple of (list of movie rows, total count)
    """
    ***REMOVED*** Base query
    query = """
    SELECT m.*
    FROM movie m
    """

    ***REMOVED*** Start building WHERE clauses and parameters
    where_clauses = []
    params: Dict[str, Any] = {}

    ***REMOVED*** Add title search condition
    search_pattern = f"%{title_search}%"
    where_clauses.append("LOWER(m.title) LIKE LOWER(:title_search)")
    params["title_search"] = search_pattern

    ***REMOVED*** If filtering by genre, join with genre table
    if genre_id is not None:
        query += """
        JOIN movie_genre_link mgl ON m.id = mgl.movie_id 
        JOIN genre g ON mgl.genre_id = g.id
        """
        where_clauses.append("mgl.genre_id = :genre_id")
        params["genre_id"] = genre_id

    ***REMOVED*** Add WHERE clause with all conditions
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    ***REMOVED*** Add sorting
    valid_sort_fields = ["title", "release_date", "imdb_rating", "vote_count"]
    sort_field = sort_by if sort_by in valid_sort_fields else "title"

    query += f" ORDER BY m.{sort_field}"
    if sort_desc:
        query += " DESC"
    else:
        query += " ASC"

    ***REMOVED*** Add NULLS LAST for rating fields to ensure movies with ratings appear first
    if sort_field in ["imdb_rating", "vote_average", "vote_count"]:
        query += " NULLS LAST"

    ***REMOVED*** Add pagination
    query += " LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip

    ***REMOVED*** Count query - needs to match the filters of the main query
    count_query = """
    SELECT COUNT(DISTINCT m.id) 
    FROM movie m
    """

    if genre_id is not None:
        count_query += """
        JOIN movie_genre_link mgl ON m.id = mgl.movie_id 
        JOIN genre g ON mgl.genre_id = g.id
        """

    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)

    ***REMOVED*** Execute queries
    result = db_session.execute(text(query), params)
    count_result = db_session.execute(text(count_query), params)

    movies = list(result.all())
    total_count = count_result.scalar() or 0

    return movies, total_count


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


def get_genre_by_name(
    db_session: DBSession, genre_name: str
) -> Optional[Dict[str, Any]]:
    """
    Get a genre by its name (case-insensitive match).

    Args:
        db_session: SQLAlchemy database session
        genre_name: Genre name to look up

    Returns:
        Genre details dictionary or None if not found
    """
    query = """
    SELECT g.*
    FROM genre g
    WHERE LOWER(g.name) = LOWER(:genre_name)
    """

    result = db_session.execute(text(query), {"genre_name": genre_name})
    genre = result.first()

    if not genre:
        return None

    ***REMOVED*** Convert to dictionary
    return dict(genre._mapping)
