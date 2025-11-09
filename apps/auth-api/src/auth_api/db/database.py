"""Database connection and utilities for the auth API."""

from collections.abc import Generator, Iterator
from contextlib import suppress
from typing import Any

from config.logging import get_logger
from sqlalchemy import Engine, inspect
from sqlmodel import Session, SQLModel, create_engine

from auth_api.config.app import settings

logger = get_logger(__name__)

***REMOVED*** Global engine instance
_engine: Engine | None = None


def get_engine(enable_monitoring: bool = True) -> Engine:
    """Get or create the database engine.

    Args:
        enable_monitoring: Whether to enable database monitoring (default: True)

    Returns:
        SQLAlchemy engine
    """
    global _engine

    ***REMOVED*** Create engine if it doesn't exist
    if _engine is None:
        logger.info(f"Creating database engine with URL: {settings.get_database_url_masked()}")

        ***REMOVED*** Use database_echo from settings
        if settings.database_echo:
            logger.info("SQL echo is enabled - SQL statements will be logged")

        _engine = create_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
        )

    return _engine


def get_session() -> Generator[Session, None, None]:
    """Get a database session.

    Yields:
        SQLModel session
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session


def init_db(create_tables: bool = False) -> None:
    """Initialize the database.

    Args:
        create_tables: Whether to create tables based on SQLModel classes
    """
    ***REMOVED*** Get engine
    engine = get_engine()

    if create_tables:
        logger.info("Creating database tables")
        ***REMOVED*** Import models to ensure they're registered with SQLModel
        SQLModel.metadata.create_all(engine)


def init_database() -> None:
    """Initialize the database connection using the centralized settings.

    This only establishes the connection - database tables should be created
    via migrations using the shared movie-storage library or centralized management.
    """
    ***REMOVED*** Initialize database connection only - NO table creation
    ***REMOVED*** Tables should be created via the shared movie-storage library or centralized migrations
    init_db(create_tables=False)


def get_db() -> Iterator[Session]:
    """Get a database session for use in API endpoints."""
    ***REMOVED*** Use the centralized session generator
    session_generator = get_session()
    try:
        db = next(session_generator)
        yield db
    finally:
        with suppress(StopIteration):
            next(session_generator)


def check_database_schema() -> dict[str, Any]:
    """Check if database schema is properly set up.

    Returns:
        Dictionary with schema status information
    """
    try:
        engine = get_engine()
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        ***REMOVED*** Check for critical tables for auth service
        required_tables = ["user"]
        missing_tables = [table for table in required_tables if table not in table_names]

        return {
            "schema_ready": len(missing_tables) == 0,
            "existing_tables": table_names,
            "missing_tables": missing_tables,
            "required_tables": required_tables,
        }

    except Exception as e:
        return {
            "schema_ready": False,
            "error": str(e),
            "existing_tables": [],
            "missing_tables": [],
            "required_tables": [],
        }
