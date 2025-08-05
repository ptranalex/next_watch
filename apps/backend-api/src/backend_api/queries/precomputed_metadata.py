"""
Precomputed metadata queries for high-performance movie retrieval.

This module implements the Netflix-style "cache forever" pattern by using
precomputed materialized views for movie metadata aggregation.
"""

from typing import Any, Dict, List, Optional, Tuple
import json

from sqlalchemy.sql import text
from config.logging import get_logger
from backend_api.queries.common import DBSession

logger = get_logger(__name__)


def get_movies_precomputed_bulk(
    db_session: DBSession, movie_ids: List[int]
) -> List[Dict[str, Any]]:
    """
    Get complete movie metadata using precomputed materialized view.

    This follows the Netflix architecture pattern of precomputing all metadata
    during content ingestion rather than assembling it at request time.

    Args:
        db_session: SQLAlchemy database session
        movie_ids: List of movie IDs to fetch

    Returns:
        List of complete movie dictionaries with all metadata included
    """
    if not movie_ids:
        return []

    logger.debug(f"Fetching precomputed metadata for {len(movie_ids)} movies")

    ***REMOVED*** Single query to get complete precomputed metadata
    query = """
    SELECT 
        id,
        title,
        overview,
        release_date,
        runtime,
        budget,
        revenue,
        imdb_rating,
        rotten_tomatoes_rating,
        metacritic_rating,
        poster_path,
        backdrop_path,
        tmdb_id,
        imdb_id,
        popularity,
        vote_average,
        vote_count,
        adult,
        original_language,
        original_title,
        status,
        tagline,
        homepage,
        created_at,
        updated_at,
        genres,
        "cast",
        director,
        writer,
        trailer_count,
        metadata_version,
        cached_at
    FROM movie_metadata_complete
    WHERE id = ANY(:movie_ids)
    ORDER BY id
    """

    result = db_session.execute(text(query), {"movie_ids": movie_ids})
    movies = []

    for row in result.all():
        movie_dict = dict(row._mapping)

        ***REMOVED*** Handle JSON fields (SQLAlchemy auto-deserializes PostgreSQL JSON)
        try:
            ***REMOVED*** If genres is already a list/dict, keep it; if it's a string, parse it
            genres = movie_dict.get("genres")
            if isinstance(genres, str):
                movie_dict["genres"] = json.loads(genres) if genres else []
            elif genres is None:
                movie_dict["genres"] = []
            ***REMOVED*** If it's already a list/dict, keep it as-is

            ***REMOVED*** Same for cast
            cast = movie_dict.get("cast")
            if isinstance(cast, str):
                movie_dict["cast"] = json.loads(cast) if cast else []
            elif cast is None:
                movie_dict["cast"] = []
            ***REMOVED*** If it's already a list/dict, keep it as-is

        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON metadata for movie {movie_dict.get('id')}: {e}")
            movie_dict["genres"] = []
            movie_dict["cast"] = []

        movies.append(movie_dict)

    logger.debug(f"Retrieved {len(movies)} precomputed movie records")
    return movies


def get_movie_precomputed_single(db_session: DBSession, movie_id: int) -> Optional[Dict[str, Any]]:
    """
    Get single movie's complete precomputed metadata.

    Args:
        db_session: SQLAlchemy database session
        movie_id: Movie ID to fetch

    Returns:
        Complete movie dictionary or None if not found
    """
    movies = get_movies_precomputed_bulk(db_session, [movie_id])
    return movies[0] if movies else None


def get_popular_movies_precomputed(
    db_session: DBSession, limit: int = 100, skip: int = 0, min_rating: Optional[float] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get popular movies using precomputed metadata for cache warming.

    Args:
        db_session: SQLAlchemy database session
        limit: Maximum number of movies to return
        skip: Number of movies to skip for pagination
        min_rating: Minimum IMDB rating filter

    Returns:
        Tuple of (movies list, total count)
    """
    ***REMOVED*** Build WHERE clause
    where_conditions = []
    params: Dict[str, Any] = {"limit": limit, "offset": skip}

    if min_rating is not None:
        where_conditions.append("imdb_rating >= :min_rating")
        params["min_rating"] = min_rating

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    ***REMOVED*** Get movies
    movies_query = f"""
    SELECT 
        id, title, overview, release_date, runtime, budget, revenue,
        imdb_rating, rotten_tomatoes_rating, metacritic_rating,
        poster_path, backdrop_path, tmdb_id, imdb_id, popularity,
        vote_average, vote_count, adult, original_language,
        original_title, status, tagline, homepage,
        created_at, updated_at, genres, "cast", director, writer,
        trailer_count, metadata_version, cached_at
    FROM movie_metadata_complete
    {where_clause}
    ORDER BY popularity DESC, vote_average DESC
    LIMIT :limit OFFSET :offset
    """

    ***REMOVED*** Get total count
    count_query = f"""
    SELECT COUNT(*) as total
    FROM movie_metadata_complete
    {where_clause}
    """

    ***REMOVED*** Execute queries
    movies_result = db_session.execute(text(movies_query), params)
    count_result = db_session.execute(text(count_query), params)

    ***REMOVED*** Process movies
    movies = []
    for row in movies_result.all():
        movie_dict = dict(row._mapping)

        ***REMOVED*** Handle JSON fields (SQLAlchemy auto-deserializes PostgreSQL JSON)
        try:
            ***REMOVED*** If genres is already a list/dict, keep it; if it's a string, parse it
            genres = movie_dict.get("genres")
            if isinstance(genres, str):
                movie_dict["genres"] = json.loads(genres) if genres else []
            elif genres is None:
                movie_dict["genres"] = []
            ***REMOVED*** If it's already a list/dict, keep it as-is

            ***REMOVED*** Same for cast
            cast = movie_dict.get("cast")
            if isinstance(cast, str):
                movie_dict["cast"] = json.loads(cast) if cast else []
            elif cast is None:
                movie_dict["cast"] = []
            ***REMOVED*** If it's already a list/dict, keep it as-is

        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON metadata for movie {movie_dict.get('id')}: {e}")
            movie_dict["genres"] = []
            movie_dict["cast"] = []

        movies.append(movie_dict)

    ***REMOVED*** Get total count
    total_count = count_result.scalar() or 0

    logger.debug(f"Retrieved {len(movies)} popular movies (total: {total_count})")
    return movies, total_count


def check_metadata_freshness(db_session: DBSession, movie_ids: List[int]) -> Dict[int, bool]:
    """
    Check if precomputed metadata is fresh for given movie IDs.

    This helps determine if we need to refresh the materialized view
    or warm the cache for specific movies.

    Args:
        db_session: SQLAlchemy database session
        movie_ids: List of movie IDs to check

    Returns:
        Dictionary mapping movie_id -> is_fresh (bool)
    """
    if not movie_ids:
        return {}

    ***REMOVED*** Check if precomputed metadata exists and when it was last updated
    query = """
    SELECT 
        m.id,
        m.updated_at as source_updated,
        pmc.cached_at as precomputed_cached,
        pmc.metadata_version
    FROM movie m
    LEFT JOIN movie_metadata_complete pmc ON m.id = pmc.id
    WHERE m.id = ANY(:movie_ids)
    """

    result = db_session.execute(text(query), {"movie_ids": movie_ids})
    freshness = {}

    for row in result.all():
        movie_id = row.id
        source_updated = row.source_updated
        precomputed_cached = row.precomputed_cached

        ***REMOVED*** Consider fresh if:
        ***REMOVED*** 1. Precomputed data exists
        ***REMOVED*** 2. Precomputed data is newer than source data
        is_fresh = (
            precomputed_cached is not None
            and source_updated is not None
            and precomputed_cached >= source_updated
        )

        freshness[movie_id] = is_fresh

    ***REMOVED*** Mark any missing movies as not fresh
    for movie_id in movie_ids:
        if movie_id not in freshness:
            freshness[movie_id] = False

    return freshness


def refresh_movie_metadata_selective(
    db_session: DBSession, movie_ids: Optional[List[int]] = None
) -> bool:
    """
    Refresh materialized view for specific movies or completely.

    Args:
        db_session: SQLAlchemy database session
        movie_ids: Optional list of specific movie IDs to refresh
                  If None, refreshes entire materialized view

    Returns:
        True if refresh succeeded, False otherwise
    """
    try:
        if movie_ids:
            ***REMOVED*** For selective refresh, we'd need to implement a different strategy
            ***REMOVED*** since PostgreSQL materialized views don't support partial refresh
            ***REMOVED*** This could be implemented with a staging table approach
            logger.info(f"Selective refresh requested for {len(movie_ids)} movies")
            ***REMOVED*** For now, do a full refresh

        ***REMOVED*** Full refresh
        refresh_query = "SELECT refresh_movie_metadata_complete()"
        db_session.execute(text(refresh_query))
        db_session.commit()

        logger.info("Successfully refreshed movie metadata materialized view")
        return True

    except Exception as e:
        logger.error(f"Failed to refresh movie metadata: {e}")
        db_session.rollback()
        return False


def get_metadata_stats(db_session: DBSession) -> Dict[str, Any]:
    """
    Get statistics about the precomputed metadata store.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary with metadata statistics
    """
    query = """
    SELECT 
        COUNT(*) as total_movies,
        COUNT(DISTINCT jsonb_array_length(genres)) as unique_genre_counts,
        AVG(jsonb_array_length(cast)) as avg_cast_size,
        MIN(cached_at) as oldest_cache,
        MAX(cached_at) as newest_cache,
        COUNT(*) FILTER (WHERE cached_at > NOW() - INTERVAL '1 day') as cached_last_24h,
        COUNT(*) FILTER (WHERE trailer_count > 0) as movies_with_trailers
    FROM movie_metadata_complete
    """

    result = db_session.execute(text(query))
    row = result.first()

    if row:
        return dict(row._mapping)
    else:
        return {
            "total_movies": 0,
            "unique_genre_counts": 0,
            "avg_cast_size": 0,
            "oldest_cache": None,
            "newest_cache": None,
            "cached_last_24h": 0,
            "movies_with_trailers": 0,
        }
