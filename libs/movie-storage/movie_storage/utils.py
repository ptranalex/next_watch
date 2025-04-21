"""Utility functions for movie storage."""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from movie_storage.config.app import Config
from movie_storage.config.logging import configure_logging
from movie_storage.db import init_db
from movie_storage.db.migrations import run_migration

logger = logging.getLogger(__name__)


def setup_movie_storage(
    database_url: Optional[str] = None,
    create_tables: bool = False,
    run_migrations: bool = False,
    log_dir: Optional[Path] = None,
    log_level: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
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
    ***REMOVED*** Create config instance
    config = Config()

    ***REMOVED*** Override database URL if provided
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Set up logging
    logging_info = configure_logging(
        config=config,
        log_dir=log_dir,
        log_level=log_level,
        verbose=verbose,
        quiet=quiet,
    )

    ***REMOVED*** Initialize database
    init_db(create_tables=create_tables, config=config)

    ***REMOVED*** Run database migrations if requested
    if run_migrations:
        logger.info("Running database migrations")
        run_migration(config=config)
        logger.info("Database migrations completed")

    logger.info(
        f"Movie storage set up with database URL: {config._mask_database_password(config.database_url)}"
    )

    ***REMOVED*** Return setup information
    return {
        "config": config,
        "logging": logging_info,
        "database_url": config.database_url,
    }
