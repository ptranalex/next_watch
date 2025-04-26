"""
Query implementations for retrieving top-rated movies.
"""

from sqlalchemy.sql import text
from typing import List, Tuple, Dict, Any, Optional, Union
import logging

from backend_api.queries.common import DBSession

logger = logging.getLogger(__name__)


def get_top_rated_movies(
    db_session: DBSession,
    year: Optional[int] = None,
    all_time: bool = False,
    genre_id: Optional[int] = None,
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
        genre_id: Optional genre ID to filter by
        limit: Maximum number of results to return
        page: Page number for pagination
        min_votes: Minimum number of votes required (for all_time queries)

    Returns:
        Tuple of (list of movie rows, total count)
    """
    ***REMOVED*** Default to current year if not all_time and no year specified
    if not all_time and year is None:
        from datetime import datetime

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
    if genre_id:
        query += " AND g.id = :genre_id"
        params["genre_id"] = genre_id

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

    if genre_id:
        count_query += " AND g.id = :genre_id"

    ***REMOVED*** Execute queries
    result = db_session.execute(text(query), params)
    count_result = db_session.execute(text(count_query), params)

    movies = list(result.all())  ***REMOVED*** Convert to List
    total_count = count_result.scalar() or 0

    return movies, total_count
