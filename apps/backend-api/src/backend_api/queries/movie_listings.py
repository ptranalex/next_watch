"""
Query implementations for retrieving lists of movies with various filtering options.
"""

from sqlalchemy.sql import text
from typing import List, Tuple, Dict, Any, Optional, Union
import logging

from backend_api.queries.common import DBSession

logger = logging.getLogger(__name__)


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
