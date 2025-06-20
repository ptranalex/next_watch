"""Migration to rename moviegenrelink table to movie_genre_link.

This migration renames the 'moviegenrelink' table to 'movie_genre_link'
to ensure consistent naming conventions between the SQL queries and the database.
"""

import logging

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError

***REMOVED*** Migration identification
MIGRATION_ID = "004_rename_moviegenrelink_table"
MIGRATION_DESCRIPTION = "Rename moviegenrelink table to movie_genre_link"

logger = logging.getLogger(__name__)


def upgrade(engine, config=None):
    """Upgrade database schema to match the current version.

    Args:
        engine: SQLAlchemy engine
        config: Config instance (optional)
    """
    logger.info("Renaming 'moviegenrelink' table to 'movie_genre_link'")

    with engine.begin() as conn:
        inspector = inspect(engine)

        ***REMOVED*** Check if the old table exists first - works across all database types
        old_table_exists = "moviegenrelink" in inspector.get_table_names()

        ***REMOVED*** Only rename if the old table exists
        if old_table_exists:
            ***REMOVED*** Use appropriate SQL for the database type
            if engine.dialect.name == "sqlite":
                conn.execute(text("ALTER TABLE moviegenrelink RENAME TO movie_genre_link"))
            else:
                ***REMOVED*** PostgreSQL and most others use this syntax
                conn.execute(text("ALTER TABLE moviegenrelink RENAME TO movie_genre_link"))

            logger.info("Table renamed successfully")

            ***REMOVED*** Record the migration
            try:
                conn.execute(
                    text("INSERT INTO migrations (id, description) VALUES (:id, :description)"),
                    {"id": MIGRATION_ID, "description": MIGRATION_DESCRIPTION},
                )
            except (OperationalError, ProgrammingError):
                logger.warning("Could not record migration - migrations table might not exist yet")
        else:
            ***REMOVED*** Check if the new table name already exists
            new_table_exists = "movie_genre_link" in inspector.get_table_names()

            if new_table_exists:
                logger.info("Target table 'movie_genre_link' already exists, skipping rename")
                ***REMOVED*** Record the migration as complete even though no changes were made
                try:
                    conn.execute(
                        text("INSERT INTO migrations (id, description) VALUES (:id, :description)"),
                        {
                            "id": MIGRATION_ID,
                            "description": MIGRATION_DESCRIPTION + " (no changes needed)",
                        },
                    )
                except (OperationalError, ProgrammingError):
                    logger.warning(
                        "Could not record migration - migrations table might not exist yet"
                    )
            else:
                logger.warning("Neither 'moviegenrelink' nor 'movie_genre_link' tables exist!")


def downgrade(engine, config=None):
    """Downgrade database schema to the previous version.

    Args:
        engine: SQLAlchemy engine
        config: Config instance (optional)
    """
    logger.info("Renaming 'movie_genre_link' table back to 'moviegenrelink'")

    with engine.begin() as conn:
        inspector = inspect(engine)

        ***REMOVED*** Check if the new table exists first
        table_exists = "movie_genre_link" in inspector.get_table_names()

        ***REMOVED*** Only rename if the new table exists
        if table_exists:
            ***REMOVED*** Use appropriate SQL for the database type
            if engine.dialect.name == "sqlite":
                conn.execute(text("ALTER TABLE movie_genre_link RENAME TO moviegenrelink"))
            else:
                ***REMOVED*** PostgreSQL and most others use this syntax
                conn.execute(text("ALTER TABLE movie_genre_link RENAME TO moviegenrelink"))

            logger.info("Table renamed back to original name")

            ***REMOVED*** Remove the migration record
            try:
                conn.execute(
                    text("DELETE FROM migrations WHERE id = :id"),
                    {"id": MIGRATION_ID},
                )
            except (OperationalError, ProgrammingError):
                logger.warning(
                    "Could not remove migration record - migrations table might not exist"
                )
        else:
            logger.warning("Table 'movie_genre_link' doesn't exist, nothing to downgrade")
