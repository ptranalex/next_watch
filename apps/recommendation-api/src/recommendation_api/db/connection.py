"""Database connection management for the Recommendation API service."""

import logging
from typing import Generator, Union
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine as sqlmodel_create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from recommendation_api.config import settings

logger = logging.getLogger(__name__)

***REMOVED*** Create engine and session factory
_engine: Union[Engine, None] = None
_session_factory = None


def get_db_engine() -> Engine:
    """Get the database engine instance.
    
    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        logger.info("Creating database engine")
        _engine = sqlmodel_create_engine(settings.database_url)
        logger.info("Database engine created successfully")
    return _engine


def get_db_session() -> Session:
    """Get a database session (dependency injection for FastAPI).
    
    Yields:
        SQLModel session instance
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_db_engine(),
            class_=Session
        )
    return _session_factory()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get a database session context manager for CLI operations.
    
    Yields:
        SQLModel session instance
    """
    engine = get_db_engine()
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


def test_connection() -> bool:
    """Test database connectivity.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def close_connections() -> None:
    """Close all database connections (useful for testing)."""
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None
    logger.info("Database connections closed") 