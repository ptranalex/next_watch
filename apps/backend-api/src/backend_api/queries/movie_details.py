"""
Query implementations for retrieving detailed information about movies.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.sql import text

from config.logging import get_logger
from backend_api.queries.common import DBSession

logger = get_logger(__name__)


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


def get_movie_genres_bulk(
    db_session: DBSession, movie_ids: List[int]
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Get genres for multiple movies in a single query (bulk operation).

    This eliminates N+1 query problems when fetching genres for multiple movies.

    Args:
        db_session: SQLAlchemy database session
        movie_ids: List of movie IDs to fetch genres for

    Returns:
        Dictionary mapping movie_id -> list of genre dictionaries
        Movies with no genres will have an empty list
    """
    if not movie_ids:
        return {}

    ***REMOVED*** Single query to get all genres for all movies
    query = """
    SELECT g.*, mgl.movie_id
    FROM genre g
    JOIN movie_genre_link mgl ON g.id = mgl.genre_id
    WHERE mgl.movie_id = ANY(:movie_ids)
    ORDER BY mgl.movie_id, g.name
    """

    result = db_session.execute(text(query), {"movie_ids": movie_ids})

    ***REMOVED*** Group genres by movie_id
    genres_by_movie: Dict[int, List[Dict[str, Any]]] = {}

    ***REMOVED*** Initialize all movie IDs with empty lists
    for movie_id in movie_ids:
        genres_by_movie[movie_id] = []

    ***REMOVED*** Populate with actual genre data
    for row in result.all():
        movie_id = row.movie_id
        genre_data = {key: value for key, value in row._mapping.items() if key != "movie_id"}
        genres_by_movie[movie_id].append(genre_data)

    return genres_by_movie


def get_movie_details_by_id(db_session: DBSession, movie_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific movie by its ID.

    Optimized version that eliminates subqueries for better performance.

    Args:
        db_session: SQLAlchemy database session
        movie_id: Movie ID

    Returns:
        Movie details dictionary or None if not found
    """
    ***REMOVED*** Get basic movie information
    movie_query = """
    SELECT m.*
    FROM movie m
    WHERE m.id = :movie_id
    """

    result = db_session.execute(text(movie_query), {"movie_id": movie_id})
    movie = result.first()

    if not movie:
        return None

    ***REMOVED*** Get director and writer information with optimized query using LIMIT
    ***REMOVED*** This query will be much faster with the new composite index
    director_query = """
    SELECT c.name
    FROM credit c
    WHERE c.movie_id = :movie_id
    AND c.department = 'Directing'
    AND c.job = 'Director'
    LIMIT 1
    """

    writer_query = """
    SELECT c.name
    FROM credit c
    WHERE c.movie_id = :movie_id
    AND c.department = 'Writing'
    AND c.job = 'Screenplay'
    LIMIT 1
    """

    ***REMOVED*** Execute both queries
    director_result = db_session.execute(text(director_query), {"movie_id": movie_id})
    writer_result = db_session.execute(text(writer_query), {"movie_id": movie_id})

    director = director_result.scalar()
    writer = writer_result.scalar()

    ***REMOVED*** Get all credits for completeness
    all_credits_query = """
    SELECT c.*
    FROM credit c
    WHERE c.movie_id = :movie_id
    """

    all_credits_result = db_session.execute(text(all_credits_query), {"movie_id": movie_id})
    credits = [dict(row._mapping) for row in all_credits_result.all()]

    ***REMOVED*** Combine movie and credits
    movie_dict = dict(movie._mapping)
    movie_dict["director"] = director
    movie_dict["writer"] = writer
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

    Optimized version that eliminates N+1 query problems by using bulk operations
    instead of subqueries for director/writer information.

    Args:
        db_session: SQLAlchemy database session
        movie_ids: List of movie IDs to fetch

    Returns:
        List of movie details dictionaries
    """
    if not movie_ids:
        return []

    ***REMOVED*** Step 1: Get basic movie information using PostgreSQL ANY() for better performance
    movie_query = """
    SELECT m.*
    FROM movie m
    WHERE m.id = ANY(:movie_ids)
    ORDER BY m.id
    """

    movie_result = db_session.execute(text(movie_query), {"movie_ids": movie_ids})
    movies = [dict(row._mapping) for row in movie_result.all()]

    if not movies:
        return []

    ***REMOVED*** Step 2: Bulk fetch director and writer information for all movies
    credits_query = """
    SELECT 
        c.movie_id,
        c.name,
        c.department,
        c.job
    FROM credit c
    WHERE c.movie_id = ANY(:movie_ids)
    AND c.department IN ('Directing', 'Writing')
    AND c.job IN ('Director', 'Screenplay')
    ORDER BY c.movie_id, c.department, c.job
    """

    credits_result = db_session.execute(text(credits_query), {"movie_ids": movie_ids})

    ***REMOVED*** Organize credits by movie_id
    directors_by_movie = {}
    writers_by_movie = {}

    for row in credits_result.all():
        movie_id = row.movie_id
        if row.department == "Directing" and row.job == "Director":
            if movie_id not in directors_by_movie:
                directors_by_movie[movie_id] = row.name
        elif row.department == "Writing" and row.job == "Screenplay":
            if movie_id not in writers_by_movie:
                writers_by_movie[movie_id] = row.name

    ***REMOVED*** Step 3: Add director and writer information to movies
    for movie in movies:
        movie_id = movie["id"]
        movie["director"] = directors_by_movie.get(movie_id)
        movie["writer"] = writers_by_movie.get(movie_id)

    return movies
