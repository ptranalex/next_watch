"""
from config.logging import get_logger
Migration for adding the users table.

This migration adds support for user authentication.
"""

from typing import Any

from config.logging import get_logger
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

# Migration identification
MIGRATION_ID = "007_add_users_table"
MIGRATION_DESCRIPTION = "Add users table for authentication"

logger = get_logger(__name__)


def upgrade(engine: Engine) -> None:
    """
    Upgrade database to this revision.

    Args:
        engine: SQLAlchemy engine instance
        config: Optional configuration instance
    """
    logger.info("Creating users table")

    with engine.begin() as conn:
        # Create users table
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS "user" (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    username VARCHAR(255),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

        # Create index on email
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email)'))

        # Create index on username
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username)'))

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
    """
    Downgrade database from this revision.

    Args:
        engine: SQLAlchemy engine instance
        config: Optional configuration instance
    """
    logger.info("Dropping users table")

    with engine.begin() as conn:
        # Drop the users table
        conn.execute(text('DROP TABLE IF EXISTS "user"'))

        # Remove the migration record
        try:
            conn.execute(
                text("DELETE FROM migrations WHERE id = :id"),
                {"id": MIGRATION_ID},
            )
            logger.info("Migration record removed from the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not remove migration record - {str(e)}")


def get_revision_info() -> dict[str, Any]:
    """
    Get revision metadata.

    Returns:
        Dictionary with revision metadata
    """
    return {
        "revision": 7,
        "parent": 6,
        "description": MIGRATION_DESCRIPTION,
        "requires": [],
        "date_created": "2023-06-18T10:00:00Z",
    }


def get_affected_tables() -> list[str]:
    """
    Get list of affected tables.

    Returns:
        List of table names affected by this migration
    """
    return ["user"]
