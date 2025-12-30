"""Migration to create initial database tables."""

from datetime import UTC, datetime

from config.logging import get_logger
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    text,
)
from sqlalchemy.engine import Engine

logger = get_logger(__name__)

MIGRATION_ID = "001_create_initial_tables"
MIGRATION_DESCRIPTION = "Create initial movie and genre tables"


def upgrade(engine: Engine) -> None:
    """Run the upgrade migration.

    Args:
        engine: SQLAlchemy engine
    """
    metadata = MetaData()

    # Create genre table
    Table(
        "genre",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("tmdb_id", Integer, unique=True, index=True),
    )

    # Create movie table with base fields
    Table(
        "movie",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("tmdb_id", Integer, nullable=False, unique=True, index=True),
        Column("imdb_id", String, index=True),
        Column("title", String, nullable=False),
        Column("original_title", String),
        Column("overview", String),
        Column("language", String),
        Column("release_date", DateTime),
        Column("runtime", Integer),
        Column("poster_url", String),
        Column("backdrop_url", String),
        Column("tmdb_rating", Float(precision=2)),
        Column("imdb_rating", Float(precision=2)),
        Column("popularity", Float(precision=2)),
        Column("budget", Integer),
        Column("revenue", Integer),
        Column("created_at", DateTime),
        Column("updated_at", DateTime),
    )

    # Create link table for many-to-many relationship
    Table(
        "moviegenrelink",
        metadata,
        Column("movie_id", Integer, ForeignKey("movie.id"), primary_key=True),
        Column("genre_id", Integer, ForeignKey("genre.id"), primary_key=True),
    )

    # Create migrations table if it doesn't exist yet
    Table(
        "migrations",
        metadata,
        Column("id", String, primary_key=True),
        Column("description", String),
        Column("applied_at", DateTime),
    )

    # Create all tables
    metadata.create_all(engine)

    # Record the migration
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO migrations (id, description, applied_at) VALUES (:id, :description, :applied_at)"
            ),
            {
                "id": MIGRATION_ID,
                "description": MIGRATION_DESCRIPTION,
                "applied_at": datetime.now(UTC),
            },
        )

    logger.info(f"Applied migration: {MIGRATION_ID}")


def downgrade(engine: Engine) -> None:
    """Run the downgrade migration.

    Args:
        engine: SQLAlchemy engine
    """
    with engine.begin() as conn:
        # Drop tables in reverse order
        conn.execute(text("DROP TABLE IF EXISTS moviegenrelink"))
        conn.execute(text("DROP TABLE IF EXISTS movie"))
        conn.execute(text("DROP TABLE IF EXISTS genre"))

        # Remove the migration record
        conn.execute(
            text("DELETE FROM migrations WHERE id = :id"),
            {"id": MIGRATION_ID},
        )

    logger.info(f"Reverted migration: {MIGRATION_ID}")
