"""Database connection utilities."""

import logging
from collections.abc import Generator

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from movie_storage.config.app import Config

logger = logging.getLogger(__name__)

***REMOVED*** Global variables
engine = None


def get_engine(db_url: str | None = None, config: Config | None = None) -> Engine:
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

    ***REMOVED*** Create new engine if needed or if a specific URL is requested
    should_create_new = engine is None
    if db_url is not None and db_url != config.database_url:
        should_create_new = True

    if should_create_new:
        logger.info(f"Creating new database engine with URL: {config._mask_database_password(url)}")

        ***REMOVED*** Use database_echo from config, but default to False for safety
        ***REMOVED*** Set DATABASE_ECHO=true in .env/.env.local to enable SQL logging
        echo_sql = False
        if config.database_echo:
            logger.info("SQL echo is enabled - SQL statements will be logged")
            echo_sql = True

        engine = create_engine(
            url,
            echo=echo_sql,
            pool_size=config.database_pool_size,
            max_overflow=config.database_max_overflow,
            pool_timeout=config.database_pool_timeout,
        )

    ***REMOVED*** At this point, engine should never be None
    if engine is None:
        raise RuntimeError("Failed to create database engine")

    return engine


def get_session(
    db_url: str | None = None, config: Config | None = None
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
    db_url: str | None = None,
    create_tables: bool = False,
    config: Config | None = None,
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
