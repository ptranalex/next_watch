"""Migration to add user movie interactions table."""

import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

***REMOVED*** Migration identification
MIGRATION_ID = "008_add_user_movie_interactions_table"
MIGRATION_DESCRIPTION = "Add user movie interactions table"

logger = logging.getLogger(__name__)


def upgrade(engine: Engine, config: Optional[Any] = None) -> None:
    """
    Create user_movie_interactions table.

    Args:
        engine: SQLAlchemy engine instance
        config: Optional configuration instance
    """
    logger.info("Creating user_movie_interactions table")
    meta = MetaData()
    meta.reflect(bind=engine)

    ***REMOVED*** Create user_movie_interactions table
    Table(
        "user_movie_interactions",
        meta,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("user.id"), nullable=False, index=True),
        Column("movie_id", Integer, ForeignKey("movie.id"), nullable=False, index=True),
        Column("watched", Boolean, nullable=False, default=False),
        Column("liked", Boolean, nullable=False, default=False),
        Column("in_watchlist", Boolean, nullable=False, default=False),
        Column("created_at", DateTime, nullable=False, default=datetime.utcnow()),
        Column("updated_at", DateTime, nullable=False, default=datetime.utcnow()),
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_interaction"),
    )

    meta.create_all(engine)
    logger.info("Created user_movie_interactions table")

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


def downgrade(engine: Engine, config: Optional[Any] = None) -> None:
    """
    Drop user_movie_interactions table.

    Args:
        engine: SQLAlchemy engine instance
        config: Optional configuration instance
    """
    logger.info("Dropping user_movie_interactions table")
    meta = MetaData()
    meta.reflect(bind=engine)

    if "user_movie_interactions" in meta.tables:
        user_movie_interactions_table = meta.tables["user_movie_interactions"]
        user_movie_interactions_table.drop(engine)
        logger.info("Dropped user_movie_interactions table")
    else:
        logger.warning("user_movie_interactions table does not exist")

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
        "revision": 8,
        "parent": 7,
        "description": MIGRATION_DESCRIPTION,
        "requires": [],
        "date_created": "2023-06-25T10:00:00Z",
    }


def get_affected_tables() -> List[str]:
    """
    Get list of affected tables.

    Returns:
        List of table names affected by this migration
    """
    return ["user_movie_interactions"]
