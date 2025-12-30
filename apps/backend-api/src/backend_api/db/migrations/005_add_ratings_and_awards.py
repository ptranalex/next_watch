"""Migration to add ratings and awards columns to the movie table.

from config.logging import get_logger
This migration adds new columns for Rotten Tomatoes rating, Metacritic rating,
and awards information to the movie table.
"""

from config.logging import get_logger
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

# Migration identification
MIGRATION_ID = "005_add_ratings_and_awards"
MIGRATION_DESCRIPTION = "Add Rotten Tomatoes, Metacritic ratings and awards columns"

logger = get_logger(__name__)


def upgrade(engine: Engine) -> None:
    """Upgrade database schema to add new rating and awards columns.

    Args:
        engine: SQLAlchemy engine
        config: Config instance (optional)
    """
    logger.info("Adding new rating and awards columns to movie table")

    with engine.begin() as conn:
        # Add new rating columns
        conn.execute(
            text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS rotten_tomatoes_rating INTEGER")
        )
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS metacritic_rating INTEGER"))
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS awards TEXT"))

        # Record the migration
        try:
            conn.execute(
                text("INSERT INTO migrations (id, description) VALUES (:id, :description)"),
                {"id": MIGRATION_ID, "description": MIGRATION_DESCRIPTION},
            )
            logger.info("Migration recorded in the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not record migration - {str(e)}")


def downgrade(engine: Engine) -> None:
    """Downgrade by removing the added columns.

    Args:
        engine: SQLAlchemy engine
        config: Config instance (optional)
    """
    logger.info("Removing rating and awards columns from movie table")

    with engine.begin() as conn:
        # Remove the added columns
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS rotten_tomatoes_rating"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS metacritic_rating"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS awards"))

        # Remove the migration record
        try:
            conn.execute(
                text("DELETE FROM migrations WHERE id = :id"),
                {"id": MIGRATION_ID},
            )
            logger.info("Migration record removed from the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not remove migration record - {str(e)}")
