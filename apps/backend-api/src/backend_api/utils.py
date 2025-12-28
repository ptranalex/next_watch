"""Utility functions for movie storage."""

from pathlib import Path
from typing import Any

from config.logging import get_logger

from backend_api.config import Config
from backend_api.db import init_db
from backend_api.db.migrations import run_migration

logger = get_logger(__name__)


def setup_backend_api_storage(
    database_url: str | None = None,
    create_tables: bool = False,
    run_migrations: bool = False,
    log_dir: Path | None = None,
    log_level: str | None = None,
    verbose: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    """Set up backend API storage with configuration, logging, and database.

    Args:
        database_url: Database connection URL (optional)
        create_tables: Whether to create database tables
        run_migrations: Whether to run database migrations
        log_dir: Directory for log files (optional)
        log_level: Log level override (optional)
        verbose: Whether to enable verbose logging
        quiet: Whether to suppress most logging

    Returns:
        Dictionary with setup information
    """
    ***REMOVED*** Create config instance
    config = Config()

    ***REMOVED*** Override database URL if provided
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Initialize database
    init_db(create_tables=create_tables)

    ***REMOVED*** Run database migrations if requested
    if run_migrations:
        logger.info("Running database migrations")
        run_migration(db_url=config.database_url if database_url else None)
        logger.info("Database migrations completed")

    logger.info(
        f"Backend API storage set up with database URL: {config.get_database_url_masked()}"
    )

    ***REMOVED*** Return setup information
    return {
        "config": config,
        "database_url": config.database_url,
    }
