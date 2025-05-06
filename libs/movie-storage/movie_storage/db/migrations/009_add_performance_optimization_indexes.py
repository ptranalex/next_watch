"""
Migration to add performance optimization indexes.

This migration adds several indexes to improve query performance for common access patterns:
1. User movie interactions filtering (watchlist, watched, liked)
2. Movie filtering by release year and ratings
3. Text search on movie titles
4. Optimized sorting indexes
5. Relationship indexing for genre and credits
"""

import logging
from typing import Dict, Any, List
from sqlalchemy import text, MetaData
from sqlalchemy.exc import OperationalError, ProgrammingError

***REMOVED*** Migration identification
MIGRATION_ID = "009_add_performance_optimization_indexes"
MIGRATION_DESCRIPTION = "Add performance optimization indexes"

logger = logging.getLogger(__name__)


def upgrade(engine, config=None):
    """
    Add performance optimization indexes.

    Args:
        engine: SQLAlchemy engine instance
        config: Optional configuration instance
    """
    logger.info("Adding performance optimization indexes")

    ***REMOVED*** Create metadata
    meta = MetaData()
    meta.reflect(bind=engine)

    ***REMOVED*** Execute SQL queries to create indexes
    with engine.begin() as conn:
        ***REMOVED*** User interaction indexes for faster watchlist, watched, and liked queries
        logger.info("Creating index on user_movie_interactions")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_user_movie_flags 
            ON user_movie_interactions (user_id, watched, liked, in_watchlist)
        """
            )
        )

        ***REMOVED*** Create index for filtering movies by release year
        logger.info("Creating index for release year filtering")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_release_year 
            ON movie (EXTRACT(YEAR FROM release_date))
        """
            )
        )

        ***REMOVED*** Create index for filtering by ratings
        logger.info("Creating index for ratings filtering")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_ratings 
            ON movie (imdb_rating, rotten_tomatoes_rating, metacritic_rating)
        """
            )
        )

        ***REMOVED*** Add trigram index for title search (requires pg_trgm extension)
        logger.info("Creating index for title text search")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_title_gin 
            ON movie USING gin (title gin_trgm_ops)
        """
            )
        )

        ***REMOVED*** Optimized indexes for common sorting patterns
        logger.info("Creating sorting indexes")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_sort_imdb 
            ON movie (imdb_rating DESC NULLS LAST, id)
        """
            )
        )
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_sort_release 
            ON movie (release_date DESC NULLS LAST, id)
        """
            )
        )
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_sort_popularity 
            ON movie (popularity DESC NULLS LAST, id)
        """
            )
        )

        ***REMOVED*** Indexes for genre filtering
        logger.info("Creating movie-genre relationship indexes")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_genre_movie 
            ON movie_genre_link (movie_id)
        """
            )
        )
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_genre_genre 
            ON movie_genre_link (genre_id)
        """
            )
        )

        ***REMOVED*** Index for credits filtering (actors in movies)
        logger.info("Creating index for actor-movie filtering")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_credit_tmdb_person 
            ON credit (tmdb_person_id) WHERE department = 'Acting'
        """
            )
        )

        ***REMOVED*** Index for TMDB ID lookups
        logger.info("Creating index for TMDB ID lookups")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_movie_tmdb_id 
            ON movie (tmdb_id)
        """
            )
        )

    ***REMOVED*** Record the migration
    with engine.begin() as conn:
        try:
            conn.execute(
                text(
                    "INSERT INTO migrations (id, description) VALUES (:id, :description)"
                ),
                {"id": MIGRATION_ID, "description": MIGRATION_DESCRIPTION},
            )
            logger.info("Migration recorded in the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not record migration - {str(e)}")


def downgrade(engine, config=None):
    """
    Remove performance optimization indexes.

    Args:
        engine: SQLAlchemy engine instance
        config: Optional configuration instance
    """
    logger.info("Removing performance optimization indexes")

    ***REMOVED*** Drop all created indexes
    with engine.begin() as conn:
        conn.execute(text("DROP INDEX IF EXISTS idx_user_movie_flags"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_release_year"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_ratings"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_title_gin"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_sort_imdb"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_sort_release"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_sort_popularity"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_genre_movie"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_genre_genre"))
        conn.execute(text("DROP INDEX IF EXISTS idx_credit_tmdb_person"))
        conn.execute(text("DROP INDEX IF EXISTS idx_movie_tmdb_id"))

    ***REMOVED*** Remove the migration record
    with engine.begin() as conn:
        try:
            conn.execute(
                text("DELETE FROM migrations WHERE id = :id"),
                {"id": MIGRATION_ID},
            )
            logger.info("Migration record removed from the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not remove migration record - {str(e)}")


def get_revision_info() -> Dict[str, Any]:
    """
    Get revision metadata.

    Returns:
        Dictionary with revision metadata
    """
    return {
        "revision": 9,
        "parent": 8,
        "description": MIGRATION_DESCRIPTION,
        "requires": [],
        "date_created": "2023-10-15T10:00:00Z",
    }


def get_affected_tables() -> List[str]:
    """
    Get list of affected tables.

    Returns:
        List of table names affected by this migration
    """
    return ["user_movie_interactions", "movie", "movie_genre_link", "credit"]
