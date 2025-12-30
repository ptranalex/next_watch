"""Migration to add Credits table and extend Movie fields."""

from datetime import UTC, datetime

from config.logging import get_logger
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = get_logger(__name__)

MIGRATION_ID = "002_add_credits_and_extended_movie_fields"
MIGRATION_DESCRIPTION = "Add Credits table and extend Movie fields with additional TMDB data"


def upgrade(engine: Engine) -> None:
    """Run the upgrade migration.

    Args:
        engine: SQLAlchemy engine
        config: Optional Config object
    """
    # First, check if movie table exists
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'movie')"
            )
        )
        movie_table_exists = result.scalar()

    if not movie_table_exists:
        logger.warning("Movie table does not exist. Creating it before applying migration.")
        # Create the movie table with basic structure using direct SQL
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE movie (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR NOT NULL,
                        release_date DATE,
                        overview TEXT,
                        poster_path VARCHAR,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )
        logger.info("Created movie table")

    # Add new columns to the movie table
    with engine.begin() as conn:
        # New basic information columns
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS tagline TEXT"))
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS status TEXT"))

        # New language and country columns
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS original_language TEXT"))
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS origin_country TEXT"))

        # New collection columns
        conn.execute(
            text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS belongs_to_collection_id INTEGER")
        )
        conn.execute(
            text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS belongs_to_collection_name TEXT")
        )

        # New URL and path columns
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS homepage TEXT"))

        # New performance metrics
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS vote_average FLOAT"))
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS vote_count INTEGER"))

        # New boolean flags
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS adult BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE movie ADD COLUMN IF NOT EXISTS video BOOLEAN DEFAULT FALSE"))

        logger.info("Added new columns to movie table")

    # Create credit table directly with SQL
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS credit (
                    id SERIAL PRIMARY KEY,
                    movie_id INTEGER,
                    tmdb_person_id INTEGER,
                    name VARCHAR NOT NULL,
                    original_name VARCHAR,
                    character VARCHAR,
                    department VARCHAR,
                    job VARCHAR,
                    cast_id INTEGER,
                    "order" INTEGER,
                    gender INTEGER,
                    profile_path VARCHAR,
                    popularity FLOAT,
                    credit_id VARCHAR,
                    adult BOOLEAN DEFAULT FALSE
                )
                """
            )
        )

        # Create index on tmdb_person_id
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_credit_tmdb_person_id ON credit (tmdb_person_id)")
        )

        # Add foreign key separately
        conn.execute(
            text(
                """
                ALTER TABLE credit
                ADD CONSTRAINT fk_credit_movie_id
                FOREIGN KEY (movie_id)
                REFERENCES movie(id)
                ON DELETE CASCADE
                """
            )
        )

    logger.info("Created credit table")

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
        config: Optional Config object
    """
    with engine.begin() as conn:
        # First remove the foreign key constraint if it exists
        conn.execute(
            text(
                """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_credit_movie_id'
                ) THEN
                    ALTER TABLE credit DROP CONSTRAINT fk_credit_movie_id;
                END IF;
            END $$;
            """
            )
        )

        # Drop the credit table
        conn.execute(text("DROP TABLE IF EXISTS credit"))
        logger.info("Dropped credit table")

        # Remove added columns from movie table (only if they exist)
        # Basic information
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS tagline"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS status"))

        # Language and country
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS original_language"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS origin_country"))

        # Collection
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS belongs_to_collection_id"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS belongs_to_collection_name"))

        # URL and path
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS homepage"))

        # Performance metrics
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS vote_average"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS vote_count"))

        # Boolean flags
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS adult"))
        conn.execute(text("ALTER TABLE movie DROP COLUMN IF EXISTS video"))

        logger.info("Removed new columns from movie table")

        # Remove the migration record
        conn.execute(
            text("DELETE FROM migrations WHERE id = :id"),
            {"id": MIGRATION_ID},
        )

    logger.info(f"Reverted migration: {MIGRATION_ID}")
