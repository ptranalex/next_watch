"""Database connection management for the Recommendation API service."""

import logging
from typing import Generator, ContextManager
from contextlib import contextmanager
from sqlmodel import Session
from movie_storage.db import init_db, get_engine, get_session  ***REMOVED*** type: ignore
from movie_storage.config.app import Config  ***REMOVED*** type: ignore

from recommendation_api.config import settings

logger = logging.getLogger(__name__)


***REMOVED*** Initialize database connection
def init_database() -> None:
    """Initialize the database connection using movie-storage.

    This sets up the database connection with proper pool settings.
    """
    ***REMOVED*** Create config with enhanced pool settings
    config = Config()
    config.database_url = settings.database_url
    config.database_pool_size = 20  ***REMOVED*** Increased from default 5
    config.database_max_overflow = 30  ***REMOVED*** Increased from default 10
    config.database_pool_timeout = 60  ***REMOVED*** Increased from default 30

    ***REMOVED*** Initialize database with config
    logger.info(f"Initializing database with enhanced connection pool settings")
    logger.info(
        f"Pool size: {config.database_pool_size}, Max overflow: {config.database_max_overflow}"
    )
    init_db(db_url=settings.database_url, create_tables=False, config=config)

    ***REMOVED*** Test connection
    from sqlalchemy import text

    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Database connection test successful")


***REMOVED*** Dependency for FastAPI routes
def get_db_session() -> Generator[Session, None, None]:
    """Get a database session (dependency injection for FastAPI).

    Yields:
        SQLModel session instance
    """
    session_generator = get_session()
    try:
        db = next(session_generator)
        yield db
    finally:
        try:
            next(session_generator)
        except StopIteration:
            pass


***REMOVED*** Context manager for CLI operations
@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get a database session context manager for CLI operations.

    Yields:
        SQLModel session instance
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database context error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


***REMOVED*** Simple function to get a session directly (no context manager)
def get_simple_session() -> Session:
    """Get a simple database session (not a context manager).

    Returns:
        SQLModel session instance
    """
    engine = get_engine()
    return Session(engine)


def test_connection() -> bool:
    """Test database connectivity.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text

        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
