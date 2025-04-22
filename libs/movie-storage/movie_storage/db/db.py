"""Database connection utilities."""

import logging
from typing import Generator, Optional
from sqlmodel import Session, create_engine, SQLModel

from movie_storage.config.app import Config
from movie_storage.models import Movie, Genre, MovieGenreLink, Credit

logger = logging.getLogger(__name__)

***REMOVED*** Global variables
engine = None


def get_engine(db_url: Optional[str] = None, config: Optional[Config] = None):
    """Get or create the database engine.

    Args:
        db_url: Database connection URL (optional)
        config: Config instance (optional)

    Returns:
        SQLAlchemy engine
    """
    global engine

    ***REMOVED*** Get config if not provided
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Use provided URL or config
    url = db_url or config.database_url

    if not url:
        raise ValueError("Database URL must be provided")

    ***REMOVED*** Create new engine if needed or requested
    if engine is None or db_url is not None:
        logger.info(
            f"Creating new database engine with URL: {config._mask_database_password(url)}"
        )
        engine = create_engine(
            url,
            echo=config.database_echo,
            pool_size=config.database_pool_size,
            max_overflow=config.database_max_overflow,
            pool_timeout=config.database_pool_timeout,
        )

    return engine


def get_session(
    db_url: Optional[str] = None, config: Optional[Config] = None
) -> Generator[Session, None, None]:
    """Get a database session.

    Args:
        db_url: Database connection URL (optional)
        config: Config instance (optional)

    Yields:
        SQLModel session
    """
    engine = get_engine(db_url, config)
    with Session(engine) as session:
        yield session


def init_db(
    db_url: Optional[str] = None,
    create_tables: bool = False,
    config: Optional[Config] = None,
) -> None:
    """Initialize the database.

    Args:
        db_url: Database connection URL (optional)
        create_tables: Whether to create tables based on SQLModel classes
        config: Config instance (optional)
    """
    ***REMOVED*** Get config if not provided
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Update config with provided URL if any
    if db_url:
        config.database_url = db_url

    ***REMOVED*** Get engine with updated config
    engine = get_engine(config=config)

    if create_tables:
        logger.info("Creating database tables")
        ***REMOVED*** Import models to ensure they're registered with SQLModel
        SQLModel.metadata.create_all(engine)
