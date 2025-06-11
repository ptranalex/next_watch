"""Database migrations for the movie storage package.

This package handles database schema migrations for the movie-storage library.
Each migration is defined in a separate Python module, with a standardized
interface for upgrade and downgrade operations.

Migration files are numbered (e.g., 001_create_initial_tables.py) and applied
in sequence. Each migration is tracked in the database to ensure it's only
applied once.

To add a new migration:
1. Create a new file with the next sequence number
2. Define MIGRATION_ID and MIGRATION_DESCRIPTION constants
3. Implement upgrade() and downgrade() functions
4. Add the module to the MIGRATIONS list in this file
"""

import importlib
import logging
from typing import Dict, List, Optional

from sqlalchemy import Engine, inspect, text
from sqlmodel import Session, SQLModel, create_engine

from backend_api.config.app import Config

logger = logging.getLogger(__name__)

***REMOVED*** List of migration modules to apply in order
MIGRATIONS = [
    "backend_api.db.migrations.001_create_initial_tables",
    "backend_api.db.migrations.002_add_credits_and_extended_movie_fields",
    "backend_api.db.migrations.003_update_budget_revenue_to_bigint",
    "backend_api.db.migrations.004_rename_moviegenrelink_table",
    "backend_api.db.migrations.005_add_ratings_and_awards",
    "backend_api.db.migrations.006_add_trailer_table",
    "backend_api.db.migrations.007_add_users_table",
    "backend_api.db.migrations.008_add_user_movie_interactions_table",
    "backend_api.db.migrations.009_add_performance_optimization_indexes",
]


def get_applied_migrations(engine: Engine) -> Dict[str, str]:
    """Get a list of applied migrations from the database.

    Args:
        engine: SQLAlchemy engine

    Returns:
        Dictionary mapping migration IDs to descriptions
    """
    ***REMOVED*** First check if migrations table exists using SQLAlchemy inspector
    inspector = inspect(engine)
    table_exists = "migrations" in inspector.get_table_names()

    ***REMOVED*** If table doesn't exist, create it
    if not table_exists:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE migrations (
                        id VARCHAR(255) PRIMARY KEY,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )
        logger.info("Created migrations table")
        return {}

    ***REMOVED*** Check if table has correct schema
    try:
        ***REMOVED*** Try to query the table with expected columns
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, description FROM migrations"))
            return {row[0]: row[1] for row in result}
    except Exception as e:
        logger.warning(f"Error querying migrations table: {e}")

        ***REMOVED*** Table exists but has wrong schema - recreate it
        with engine.begin() as conn:
            ***REMOVED*** Drop the existing table
            logger.warning("Migrations table has incorrect schema, recreating it")
            conn.execute(text("DROP TABLE migrations"))

            ***REMOVED*** Create the migrations table with the correct schema
            conn.execute(
                text(
                    """
                    CREATE TABLE migrations (
                        id VARCHAR(255) PRIMARY KEY,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )
        logger.info("Recreated migrations table")
        return {}


def run_migration(db_url: Optional[str] = None, config: Optional[Config] = None) -> List[str]:
    """Run database migrations.

    Args:
        db_url: Database URL (optional)
        config: Config instance (optional)

    Returns:
        List of applied migration IDs
    """
    ***REMOVED*** Get config if not provided
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Use provided URL or config URL
    db_url = db_url or config.database_url

    ***REMOVED*** Create engine
    engine = create_engine(db_url)

    ***REMOVED*** Get applied migrations
    applied_migrations = get_applied_migrations(engine)
    logger.info(f"Found {len(applied_migrations)} applied migrations")

    ***REMOVED*** Run pending migrations
    applied_ids = []
    for migration_module in MIGRATIONS:
        try:
            ***REMOVED*** Import migration module
            module = importlib.import_module(migration_module)
            migration_id = getattr(module, "MIGRATION_ID", migration_module)

            ***REMOVED*** Skip if already applied
            if migration_id in applied_migrations:
                logger.info(f"Migration {migration_id} already applied, skipping")
                continue

            ***REMOVED*** Run migration
            logger.info(f"Applying migration: {migration_id}")
            module.upgrade(engine, config)
            applied_ids.append(migration_id)
            logger.info(f"Migration {migration_id} applied successfully")
        except Exception as e:
            logger.error(f"Error applying migration {migration_module}: {str(e)}")
            raise

    logger.info(f"Applied {len(applied_ids)} migrations")
    return applied_ids


__all__ = ["run_migration", "get_applied_migrations"]
