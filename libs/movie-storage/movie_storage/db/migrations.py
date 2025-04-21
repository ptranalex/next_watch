"""Database migration utilities."""

import logging
from typing import Optional
import sqlalchemy as sa
from sqlalchemy import text
from sqlmodel import Session

from movie_storage.db.db import get_engine, get_session
from movie_storage.config.app import Config

logger = logging.getLogger(__name__)


def run_migration(
    db_url: Optional[str] = None, config: Optional[Config] = None
) -> None:
    """Run all migrations in sequence.

    Args:
        db_url: Database connection URL (optional)
        config: Config instance (optional)
    """
    logger.info("Running database migrations")

    ***REMOVED*** Get a database connection
    engine = get_engine(db_url, config)
    dialect = engine.dialect.name

    ***REMOVED*** Create migrations table if it doesn't exist
    with engine.connect() as conn:
        ***REMOVED*** Adjust SQL syntax for different dialects
        if dialect == "sqlite":
            migrations_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        elif dialect == "postgresql":
            migrations_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            ***REMOVED*** Default for other databases
            migrations_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

        conn.execute(text(migrations_table_sql))
        conn.commit()

    ***REMOVED*** Run migrations in order
    migrations = [
        ("add_tmdb_id_to_genre", add_tmdb_id_to_genre),
        ***REMOVED*** Add future migrations here
    ]

    for name, migration_func in migrations:
        ***REMOVED*** Check if migration has already been applied
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id FROM migrations WHERE name = :name"), {"name": name}
            ).fetchone()

            ***REMOVED*** Skip if already applied
            if result:
                logger.info(f"Migration '{name}' already applied, skipping")
                continue

            ***REMOVED*** Apply migration
            logger.info(f"Applying migration '{name}'")
            try:
                migration_func(engine)

                ***REMOVED*** Record successful migration
                conn.execute(
                    text("INSERT INTO migrations (name) VALUES (:name)"), {"name": name}
                )
                conn.commit()
                logger.info(f"Migration '{name}' applied successfully")
            except Exception as e:
                logger.error(f"Error applying migration '{name}': {str(e)}")
                raise


def add_tmdb_id_to_genre(engine) -> None:
    """Add tmdb_id column to genre table.

    Args:
        engine: SQLAlchemy engine
    """
    inspector = sa.inspect(engine)

    ***REMOVED*** Check if the column already exists
    columns = [col["name"] for col in inspector.get_columns("genre")]
    if "tmdb_id" in columns:
        logger.info("Column 'tmdb_id' already exists in 'genre' table")
        return

    ***REMOVED*** Add the tmdb_id column
    with engine.begin() as conn:
        ***REMOVED*** SQLite doesn't support ALTER TABLE ADD COLUMN with constraints,
        ***REMOVED*** so we need to check the database type
        dialect = engine.dialect.name

        if dialect == "sqlite":
            ***REMOVED*** For SQLite we need multiple steps
            ***REMOVED*** 1. Create a new table with the desired schema
            conn.execute(
                text(
                    """
                CREATE TABLE genre_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    tmdb_id INTEGER UNIQUE
                )
            """
                )
            )

            ***REMOVED*** 2. Copy data from the old table
            conn.execute(
                text(
                    """
                INSERT INTO genre_new (id, name)
                SELECT id, name FROM genre
            """
                )
            )

            ***REMOVED*** 3. Drop the old table
            conn.execute(text("DROP TABLE genre"))

            ***REMOVED*** 4. Rename the new table to the original name
            conn.execute(text("ALTER TABLE genre_new RENAME TO genre"))

            ***REMOVED*** 5. Create an index on tmdb_id
            conn.execute(text("CREATE INDEX ix_genre_tmdb_id ON genre (tmdb_id)"))
        else:
            ***REMOVED*** For PostgreSQL, MySQL, etc.
            conn.execute(text("ALTER TABLE genre ADD COLUMN tmdb_id INTEGER UNIQUE"))
            conn.execute(text("CREATE INDEX ix_genre_tmdb_id ON genre (tmdb_id)"))

    logger.info("Added 'tmdb_id' column to 'genre' table")


if __name__ == "__main__":
    ***REMOVED*** This allows running the migrations directly with python -m movie_storage.db.migrations
    logging.basicConfig(level=logging.INFO)
    run_migration()
