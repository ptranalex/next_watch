"""Utility functions for movie storage."""

import logging
from pathlib import Path
from typing import Any

from movie_storage.config.app import Config
from movie_storage.config.logging import with_logging
from movie_storage.db import init_db
from movie_storage.db.migrations import run_migration

logger = logging.getLogger(__name__)


@with_logging()
def setup_movie_storage(
    database_url: str | None = None,
    create_tables: bool = False,
    run_migrations: bool = False,
    log_dir: Path | None = None,
    log_level: str | None = None,
    verbose: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    """Set up movie storage with configuration, logging, and database.

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
    # Create config instance
    config = Config()

    # Override database URL if provided
    if database_url:
        config.database_url = database_url

    # Initialize database
    init_db(create_tables=create_tables, config=config)

    # Run database migrations if requested
    if run_migrations:
        logger.info("Running database migrations")
        run_migration(config=config)
        logger.info("Database migrations completed")

    logger.info(
        f"Movie storage set up with database URL: {config._mask_database_password(config.database_url)}"
    )

    # Return setup information
    return {
        "config": config,
        "database_url": config.database_url,
    }
