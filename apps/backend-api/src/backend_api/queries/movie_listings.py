"""
Query implementations for retrieving lists of movies with various filtering options.
"""

from typing import Any

from config.logging import get_logger
from sqlalchemy.sql import text

from backend_api.queries.common import DBSession

logger = get_logger(__name__)


def get_movies_with_filters(
    db_session: DBSession,
    skip: int = 0,
    limit: int = 20,
    genre_id: int | None = None,
    actor_id: int | None = None,
    actor_tmdb_id: int | None = None,
    sort_by: str = "title",
    sort_desc: bool = False,
    imdb_rating: float | None = None,
    rotten_tomatoes_rating: int | None = None,
    metacritic_rating: int | None = None,
    year: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> tuple[list[Any], int]:
    """
    Get movies with pagination, filtering, and sorting.

    Args:
        db_session: SQLAlchemy database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        genre_id: Optional genre ID to filter by
        actor_id: Optional credit ID to filter by (unique relationship between actor and movie)
        actor_tmdb_id: Optional actor TMDB ID to filter by
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order
        imdb_rating: Minimum IMDb rating to filter by
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating to filter by
        metacritic_rating: Minimum Metacritic rating to filter by
        year: Release year to filter by
        start_year: Start release year to filter by (inclusive)
        end_year: End release year to filter by (inclusive)

    Returns:
        Tuple of (list of movie rows, total count)
    """
    ***REMOVED*** Base query
    query = """
    SELECT DISTINCT m.*
    FROM movie m
    """

    ***REMOVED*** If filtering by genre, join with genre table
    where_clauses = []
    params: dict[str, Any] = {}

    if genre_id is not None:
        query += """
        JOIN movie_genre_link mgl ON m.id = mgl.movie_id
        JOIN genre g ON mgl.genre_id = g.id
        """
        where_clauses.append("mgl.genre_id = :genre_id")
        params["genre_id"] = genre_id

    ***REMOVED*** If filtering by actor or credit, join with credit table
    if actor_id is not None or actor_tmdb_id is not None:
        query += """
        JOIN credit c ON m.id = c.movie_id
        """

        ***REMOVED*** Filter by specific credit ID
        if actor_id is not None:
            where_clauses.append("c.id = :actor_id AND c.department = 'Acting'")
            params["actor_id"] = actor_id

        ***REMOVED*** Or filter by actor's TMDB ID
        if actor_tmdb_id is not None:
            where_clauses.append("c.tmdb_person_id = :actor_tmdb_id AND c.department = 'Acting'")
            params["actor_tmdb_id"] = actor_tmdb_id

    ***REMOVED*** Add rating filters
    if imdb_rating is not None:
        where_clauses.append("m.imdb_rating >= :imdb_rating")
        params["imdb_rating"] = imdb_rating

    if rotten_tomatoes_rating is not None:
        where_clauses.append("m.rotten_tomatoes_rating >= :rotten_tomatoes_rating")
        params["rotten_tomatoes_rating"] = rotten_tomatoes_rating

    if metacritic_rating is not None:
        where_clauses.append("m.metacritic_rating >= :metacritic_rating")
        params["metacritic_rating"] = metacritic_rating

    ***REMOVED*** Add year filter
    if year is not None:
        where_clauses.append("EXTRACT(YEAR FROM m.release_date) = :year")
        params["year"] = year

    ***REMOVED*** Add year range filters
    if start_year is not None:
        where_clauses.append("EXTRACT(YEAR FROM m.release_date) >= :start_year")
        params["start_year"] = start_year

    if end_year is not None:
        where_clauses.append("EXTRACT(YEAR FROM m.release_date) <= :end_year")
        params["end_year"] = end_year

    ***REMOVED*** Add WHERE clause if we have any conditions
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    ***REMOVED*** Add sorting
    valid_sort_fields = [
        "title",
        "release_date",
        "imdb_rating",
        "rotten_tomatoes_rating",
        "metacritic_rating",
        "vote_count",
    ]
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
    count_query = """
    SELECT COUNT(DISTINCT m.id)
    FROM movie m
    """

    ***REMOVED*** If filtering by genre, join with genre table
    if genre_id is not None:
        count_query += """
        JOIN movie_genre_link mgl ON m.id = mgl.movie_id
        JOIN genre g ON mgl.genre_id = g.id
        """

    ***REMOVED*** If filtering by actor or credit, join with credit table
    if actor_id is not None or actor_tmdb_id is not None:
        count_query += """
        JOIN credit c ON m.id = c.movie_id
        """

    ***REMOVED*** Add WHERE clause if we have any conditions
    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)

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
    genre_id: int | None = None,
    actor_id: int | None = None,
    actor_tmdb_id: int | None = None,
    sort_by: str = "title",
    sort_desc: bool = False,
    imdb_rating: float | None = None,
    rotten_tomatoes_rating: int | None = None,
    metacritic_rating: int | None = None,
    year: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> tuple[list[Any], int]:
    """
    Search for movies by title with additional filtering options.

    Args:
        db_session: SQLAlchemy database session
        title_search: Title search string (case-insensitive partial match)
        skip: Number of records to skip
        limit: Maximum number of records to return
        genre_id: Optional genre ID to filter by
        actor_id: Optional credit ID to filter by (unique relationship between actor and movie)
        actor_tmdb_id: Optional actor TMDB ID to filter by
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order
        imdb_rating: Minimum IMDb rating to filter by
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating to filter by
        metacritic_rating: Minimum Metacritic rating to filter by
        year: Release year to filter by
        start_year: Start release year to filter by (inclusive)
        end_year: End release year to filter by (inclusive)

    Returns:
        Tuple of (list of movie rows, total count)
    """
    ***REMOVED*** Base query
    query = """
    SELECT DISTINCT m.*
    FROM movie m
    """

    ***REMOVED*** Start building WHERE clauses and parameters
    where_clauses = []
    params: dict[str, Any] = {}

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

    ***REMOVED*** If filtering by actor or credit, join with credit table
    if actor_id is not None or actor_tmdb_id is not None:
        query += """
        JOIN credit c ON m.id = c.movie_id
        """

        ***REMOVED*** Filter by specific credit ID
        if actor_id is not None:
            where_clauses.append("c.id = :actor_id AND c.department = 'Acting'")
            params["actor_id"] = actor_id

        ***REMOVED*** Or filter by actor's TMDB ID
        if actor_tmdb_id is not None:
            where_clauses.append("c.tmdb_person_id = :actor_tmdb_id AND c.department = 'Acting'")
            params["actor_tmdb_id"] = actor_tmdb_id

    ***REMOVED*** Add rating filters
    if imdb_rating is not None:
        where_clauses.append("m.imdb_rating >= :imdb_rating")
        params["imdb_rating"] = imdb_rating

    if rotten_tomatoes_rating is not None:
        where_clauses.append("m.rotten_tomatoes_rating >= :rotten_tomatoes_rating")
        params["rotten_tomatoes_rating"] = rotten_tomatoes_rating

    if metacritic_rating is not None:
        where_clauses.append("m.metacritic_rating >= :metacritic_rating")
        params["metacritic_rating"] = metacritic_rating

    ***REMOVED*** Add year filter
    if year is not None:
        where_clauses.append("EXTRACT(YEAR FROM m.release_date) = :year")
        params["year"] = year

    ***REMOVED*** Add year range filters
    if start_year is not None:
        where_clauses.append("EXTRACT(YEAR FROM m.release_date) >= :start_year")
        params["start_year"] = start_year

    if end_year is not None:
        where_clauses.append("EXTRACT(YEAR FROM m.release_date) <= :end_year")
        params["end_year"] = end_year

    ***REMOVED*** Add WHERE clause with all conditions
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    ***REMOVED*** Add sorting
    valid_sort_fields = [
        "title",
        "release_date",
        "imdb_rating",
        "rotten_tomatoes_rating",
        "metacritic_rating",
        "vote_count",
    ]
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

    if actor_id is not None or actor_tmdb_id is not None:
        count_query += """
        JOIN credit c ON m.id = c.movie_id
        """

    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)

    ***REMOVED*** Execute queries
    result = db_session.execute(text(query), params)
    count_result = db_session.execute(text(count_query), params)

    movies = list(result.all())
    total_count = count_result.scalar() or 0

    return movies, total_count
