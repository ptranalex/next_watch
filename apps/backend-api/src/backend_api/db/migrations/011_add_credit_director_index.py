"""
Migration to add a selective partial index for fast director lookups.

This migration adds a partial, covering index on the `credit` table to
optimize queries that retrieve the director for a given movie:

  WHERE department = 'Directing' AND job = 'Director' AND movie_id = ?

The index uses INCLUDE(name) to enable index-only scans when feasible.
"""

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

from config.logging import get_logger


MIGRATION_ID = "011_add_credit_director_index"
MIGRATION_DESCRIPTION = "Add partial covering index for Directing/Director queries on credit"

logger = get_logger(__name__)


def upgrade(engine: Engine) -> None:
    """Create the partial index for director lookups."""
    logger.info("Creating partial covering index on credit for director lookups")

    with engine.begin() as conn:
        ***REMOVED*** Create partial, covering index for director queries
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_credit_director_by_movie
                ON credit (movie_id) INCLUDE (name)
                WHERE department = 'Directing' AND job = 'Director'
                """
            )
        )

    ***REMOVED*** Record the migration
    with engine.begin() as conn:
        try:
            conn.execute(
                text("INSERT INTO migrations (id, description) VALUES (:id, :description)"),
                {"id": MIGRATION_ID, "description": MIGRATION_DESCRIPTION},
            )
            logger.info("Migration recorded in the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not record migration - {str(e)}")


def downgrade(engine: Engine) -> None:
    """Drop the partial index created by this migration."""
    logger.info("Dropping partial covering index on credit for director lookups")

    with engine.begin() as conn:
        conn.execute(text("DROP INDEX IF EXISTS idx_credit_director_by_movie"))

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
