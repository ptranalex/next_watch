"""Database connection and utilities for the backend API."""

from typing import Any, Dict, Generator, Iterator, Optional

from sqlalchemy import Engine, inspect
from sqlmodel import Session, SQLModel, create_engine

from backend_api.config.app import Config
from backend_api.config.logging import get_logger
from backend_api.models import Credit, Genre, Movie, MovieGenreLink

logger = get_logger(__name__)

***REMOVED*** Global engine instance
_engine: Optional[Engine] = None


def get_engine(config: Optional[Config] = None, enable_monitoring: bool = True) -> Engine:
    """Get or create the database engine.

    Args:
        config: Config instance (optional)
        enable_monitoring: Whether to enable database monitoring (default: True)

    Returns:
        SQLAlchemy engine
    """
    global _engine

    ***REMOVED*** Get config if not provided
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Create engine if it doesn't exist
    if _engine is None:
        logger.info(
            f"Creating database engine with URL: {config._mask_database_password(config.database_url)}"
        )

        ***REMOVED*** Use database_echo from config
        if config.database_echo:
            logger.info("SQL echo is enabled - SQL statements will be logged")

        _engine = create_engine(
            config.database_url,
            echo=config.database_echo,
            pool_size=config.database_pool_size,
            max_overflow=config.database_max_overflow,
            pool_timeout=config.database_pool_timeout,
        )

        ***REMOVED*** Enable database monitoring if requested
        if enable_monitoring and getattr(config, "database_monitoring_enabled", True):
            from backend_api.db.instrumentation import setup_database_instrumentation

            slow_threshold = getattr(config, "slow_query_threshold_ms", 100.0)
            setup_database_instrumentation(_engine, slow_threshold)
            logger.info("Database monitoring instrumentation enabled")

    return _engine


def get_session(config: Optional[Config] = None) -> Generator[Session, None, None]:
    """Get a database session.

    Args:
        config: Config instance (optional)

    Yields:
        SQLModel session
    """
    engine = get_engine(config)
    with Session(engine) as session:
        yield session


def init_db(
    create_tables: bool = False,
    config: Optional[Config] = None,
) -> None:
    """Initialize the database.

    Args:
        create_tables: Whether to create tables based on SQLModel classes
        config: Config instance (optional)
    """
    ***REMOVED*** Get config if not provided
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Get engine
    engine = get_engine(config)

    if create_tables:
        logger.info("Creating database tables")
        ***REMOVED*** Import models to ensure they're registered with SQLModel
        SQLModel.metadata.create_all(engine)


def init_database() -> None:
    """Initialize the database connection using the centralized Config system.

    This only establishes the connection - database tables should be created
    via migrations using the CLI command: python -m backend_api.scripts.setup_db run-migrations
    """
    ***REMOVED*** Get the singleton config instance which already has the proper DATABASE_URL
    config = Config.get_instance()

    ***REMOVED*** Initialize database connection only - NO table creation
    ***REMOVED*** Tables should be created via migrations in production
    init_db(create_tables=False, config=config)


def get_db() -> Iterator[Session]:
    """Get a database session for use in API endpoints."""
    ***REMOVED*** Use the centralized session generator
    session_generator = get_session()
    try:
        db = next(session_generator)
        yield db
    finally:
        try:
            next(session_generator)
        except StopIteration:
            pass


def check_database_schema(config: Optional[Config] = None) -> Dict[str, Any]:
    """Check if database schema is properly set up.

    Args:
        config: Config instance (optional)

    Returns:
        Dictionary with schema status information
    """
    if config is None:
        config = Config.get_instance()

    try:
        engine = get_engine(config=config)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        ***REMOVED*** Check for critical tables
        required_tables = ["movie", "genre", "migrations"]
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
