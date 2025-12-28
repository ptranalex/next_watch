"""Migration to update budget and revenue columns to BIGINT type.

from config.logging import get_logger
This migration alters the column types for the budget and revenue fields in the movie table
to use BIGINT instead of INTEGER, allowing for larger financial values.
"""

from config.logging import get_logger
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.sql import text

***REMOVED*** Migration identification
MIGRATION_ID = "003_update_budget_revenue_to_bigint"
MIGRATION_DESCRIPTION = "Update budget and revenue fields to BIGINT type"

logger = get_logger(__name__)


def upgrade(engine: Engine) -> None:
    """Upgrade from previous revision."""
    logger.info("Updating budget and revenue columns to BIGINT type")

    ***REMOVED*** Alter budget and revenue columns to BIGINT
    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE movie ALTER COLUMN budget TYPE BIGINT USING budget::BIGINT")
        )
        connection.execute(
            text("ALTER TABLE movie ALTER COLUMN revenue TYPE BIGINT USING revenue::BIGINT")
        )

        ***REMOVED*** Record the migration in the migrations table
        try:
            connection.execute(
                text("INSERT INTO migrations (id, description) VALUES (:id, :description)"),
                {"id": MIGRATION_ID, "description": MIGRATION_DESCRIPTION},
            )
            logger.info("Migration recorded in the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not record migration - {str(e)}")


def downgrade(engine: Engine) -> None:
    """Downgrade to previous revision."""
    logger.info("Downgrading budget and revenue columns back to INTEGER")

    ***REMOVED*** Note: Downgrading could potentially lose data if values exceed INTEGER limits
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE movie ALTER COLUMN budget TYPE INTEGER USING CASE WHEN budget > 2147483647 THEN 2147483647 ELSE budget END::INTEGER"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE movie ALTER COLUMN revenue TYPE INTEGER USING CASE WHEN revenue > 2147483647 THEN 2147483647 ELSE revenue END::INTEGER"
            )
        )

        ***REMOVED*** Remove the migration record
        try:
            connection.execute(
                text("DELETE FROM migrations WHERE id = :id"),
                {"id": MIGRATION_ID},
            )
            logger.info("Migration record removed from the database")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not remove migration record - {str(e)}")
