"""Database connection utilities."""

import logging
from typing import Generator, Optional
from sqlmodel import Session, create_engine, SQLModel

logger = logging.getLogger(__name__)

***REMOVED*** Can be configured via environment variables in a real application
DATABASE_URL: Optional[str] = None
engine = None


def get_engine(db_url: Optional[str] = None):
    """Get or create the database engine.

    Args:
        db_url: Database connection URL (optional)

    Returns:
        SQLAlchemy engine
    """
    global engine, DATABASE_URL

    ***REMOVED*** Use provided URL or the global one
    url = db_url or DATABASE_URL

    if not url:
        raise ValueError("Database URL must be provided")

    if engine is None or db_url:
        logger.info(f"Creating new database engine with URL: {url}")
        engine = create_engine(url, echo=False)

    return engine


def get_session(db_url: Optional[str] = None) -> Generator[Session, None, None]:
    """Get a database session.

    Args:
        db_url: Database connection URL (optional)

    Yields:
        SQLModel session
    """
    engine = get_engine(db_url)
    with Session(engine) as session:
        yield session


def init_db(db_url: str, create_tables: bool = False) -> None:
    """Initialize the database.

    Args:
        db_url: Database connection URL
        create_tables: Whether to create tables based on SQLModel classes
    """
    global DATABASE_URL
    DATABASE_URL = db_url
    engine = get_engine()

    if create_tables:
        logger.info("Creating database tables")
        ***REMOVED*** Import models to ensure they're registered with SQLModel
        from movie_schema.models import Movie, Genre, MovieGenreLink  ***REMOVED*** type: ignore

        SQLModel.metadata.create_all(engine)
