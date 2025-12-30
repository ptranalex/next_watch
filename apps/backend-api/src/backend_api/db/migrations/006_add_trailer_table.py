"""Migration to add the trailer table.

from config.logging import get_logger
This migration creates a new table for storing movie trailers with YouTube keys
and optional URL links.
"""

from config.logging import get_logger
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

# Migration identification
MIGRATION_ID = "006_add_trailer_table"
MIGRATION_DESCRIPTION = "Add trailer table for storing movie trailers"

logger = get_logger(__name__)


def upgrade(engine: Engine) -> None:
    """Upgrade database schema to add the trailer table.

    Args:
        engine: SQLAlchemy engine
        config: Config instance (optional)
    """
    logger.info("Creating trailer table")

    with engine.begin() as conn:
        # Create trailer table
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS trailer (
                    id SERIAL PRIMARY KEY,
                    movie_id INTEGER NOT NULL REFERENCES movie(id),
                    youtube_key VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    is_official BOOLEAN NOT NULL DEFAULT TRUE,
                    url_link VARCHAR(255),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

        # Create index on youtube_key
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_trailer_youtube_key ON trailer(youtube_key)")
        )

        # Create index on movie_id
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_trailer_movie_id ON trailer(movie_id)"))

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
    """Downgrade by removing the trailer table.

    Args:
        engine: SQLAlchemy engine
        config: Config instance (optional)
    """
    logger.info("Removing trailer table")

    with engine.begin() as conn:
        # Drop the trailer table
        conn.execute(text("DROP TABLE IF EXISTS trailer"))

        # Remove the migration record
        try:
            conn.execute(
                text("DELETE FROM migrations WHERE id = :id"),
                {"id": MIGRATION_ID},
            )
            logger.info("Migration record removed from the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not remove migration record - {str(e)}")
