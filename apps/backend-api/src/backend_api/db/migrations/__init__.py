"""Database migrations for the movie storage package.

from config.logging import get_logger
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

from config.logging import get_logger
from sqlalchemy import Engine, inspect, text
from sqlmodel import create_engine

from backend_api.config import settings

logger = get_logger(__name__)

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
    "backend_api.db.migrations.010_create_movie_metadata_materialized_view",
    "backend_api.db.migrations.011_add_credit_director_index",
]


def get_applied_migrations(engine: Engine) -> dict[str, str]:
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


def run_migration(db_url: str | None = None) -> list[str]:
    """Run database migrations.

    Args:
        db_url: Database URL (optional, uses settings.database_url if not provided)

    Returns:
        List of applied migration IDs
    """
    import time

    ***REMOVED*** Use provided URL or settings URL
    db_url = db_url or settings.database_url

    ***REMOVED*** Create engine with shorter timeout for better interruption
    engine = create_engine(db_url, pool_timeout=30, pool_recycle=3600)

    ***REMOVED*** Get applied migrations
    applied_migrations = get_applied_migrations(engine)
    logger.info(f"Found {len(applied_migrations)} applied migrations")

    ***REMOVED*** Run pending migrations
    applied_ids: list[str] = []
    for migration_module in MIGRATIONS:
        migration_start = 0.0  ***REMOVED*** Initialize before try block
        try:
            ***REMOVED*** Import migration module
            module = importlib.import_module(migration_module)
            migration_id = getattr(module, "MIGRATION_ID", migration_module)

            ***REMOVED*** Skip if already applied
            if migration_id in applied_migrations:
                logger.info(f"Migration {migration_id} already applied, skipping")
                continue

            ***REMOVED*** Run migration with timing and progress updates
            migration_start = time.time()
            logger.info(f"⏱️ Starting migration: {migration_id}")

            ***REMOVED*** Run migration (progress is shown at CLI level)
            module.upgrade(engine)

            migration_elapsed = time.time() - migration_start
            if migration_elapsed >= 60:
                minutes = int(migration_elapsed // 60)
                seconds = migration_elapsed % 60
                time_str = f"{minutes}m {seconds:.1f}s"
            else:
                time_str = f"{migration_elapsed:.1f}s"

            ***REMOVED*** Auto-record migration completion to avoid human error
            try:
                migration_description = getattr(
                    module, "MIGRATION_DESCRIPTION", migration_id
                )
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO migrations (id, description)
                            VALUES (:id, :description)
                            ON CONFLICT (id) DO NOTHING
                            """
                        ),
                        {
                            "id": migration_id,
                            "description": migration_description,
                        },
                    )
                logger.info(
                    f"📘 Recorded migration {migration_id} in migrations table (idempotent)"
                )
            except Exception as record_err:
                logger.warning(
                    f"Could not auto-record migration {migration_id}: {record_err}"
                )

            applied_ids.append(migration_id)
            logger.info(
                f"✅ Migration {migration_id} completed successfully in {time_str}"
            )

        except Exception as e:
            migration_elapsed = (
                time.time() - migration_start if migration_start > 0 else 0.0
            )
            logger.error(
                f"❌ Error applying migration {migration_module} after {migration_elapsed:.1f}s: {str(e)}"
            )
            raise

    logger.info(f"Applied {len(applied_ids)} migrations")
    return applied_ids


__all__ = ["run_migration", "get_applied_migrations"]


def downgrade_single_migration(engine: Engine, migration_id: str) -> bool:
    """Downgrade a single migration and remove its record.

    Args:
        engine: SQLAlchemy engine
        migration_id: Migration ID to downgrade (must match module filename)

    Returns:
        True if successful, False otherwise
    """
    import importlib

    logger = get_logger(__name__)

    ***REMOVED*** Import the migration module
    try:
        module = importlib.import_module(f"backend_api.db.migrations.{migration_id}")
    except ImportError as e:
        logger.error(f"Could not import migration module: {migration_id} - {str(e)}")
        return False

    ***REMOVED*** Call the downgrade function
    try:
        module.downgrade(engine)
    except Exception as e:
        logger.error(f"Failed to downgrade migration {migration_id}: {str(e)}")
        return False

    ***REMOVED*** Remove the migration record
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM migrations WHERE id = :id"), {"id": migration_id}
            )
    except Exception as e:
        logger.error(
            f"Failed to remove migration record for {migration_id} after downgrade: {str(e)}"
        )
        return False

    return True
