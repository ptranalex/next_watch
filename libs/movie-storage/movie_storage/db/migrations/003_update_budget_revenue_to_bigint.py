"""Migration to update budget and revenue columns to BIGINT type.

This migration alters the column types for the budget and revenue fields in the movie table
to use BIGINT instead of INTEGER, allowing for larger financial values.
"""

from sqlalchemy import BigInteger, Integer
from sqlalchemy.sql import text


***REMOVED*** Revision identifier
revision = "003"
down_revision = "002"


def upgrade(engine, config) -> None:
    """Upgrade from previous revision."""
    ***REMOVED*** Alter budget and revenue columns to BIGINT
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE movie ALTER COLUMN budget TYPE BIGINT USING budget::BIGINT"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE movie ALTER COLUMN revenue TYPE BIGINT USING revenue::BIGINT"
            )
        )


def downgrade(engine, config) -> None:
    """Downgrade to previous revision."""
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
