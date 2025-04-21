***REMOVED***!/usr/bin/env python3
"""Example demonstrating logging functionality in movie-storage."""

import logging
from pathlib import Path

from movie_storage.config.logging import with_logging, configure_logging
from movie_storage.config.app import Config
from movie_storage.utils import setup_movie_storage
from movie_storage.db.db import init_db

***REMOVED*** Get a logger for this module
logger = logging.getLogger(__name__)


@with_logging(log_level="DEBUG", log_dir=Path("./logs"), verbose=True)
def run_example_with_decorator():
    """Run an example using the with_logging decorator."""
    logger.info("Starting example with decorator")

    ***REMOVED*** Initialize the database
    config = Config.get_instance()

    ***REMOVED*** Log some information
    logger.debug(f"Database URL: {config._mask_database_password(config.database_url)}")
    logger.info("Database configuration loaded")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    logger.info("Example with decorator completed")


def run_example_with_direct_config():
    """Run an example using direct logging configuration."""
    ***REMOVED*** Configure logging directly
    configure_logging(
        log_level="INFO", log_dir=Path("./logs"), verbose=False, quiet=False
    )

    logger.info("Starting example with direct configuration")

    ***REMOVED*** Log some information
    logger.info("This is an info message")
    logger.debug("This debug message should not appear in console due to INFO level")

    logger.info("Example with direct configuration completed")


def main():
    """Main entry point for the example."""
    print("Running movie-storage logging examples\n")

    ***REMOVED*** Run example with decorator
    print("\n1. Example using @with_logging decorator:")
    run_example_with_decorator()

    ***REMOVED*** Run example with direct configuration
    print("\n2. Example using direct configure_logging:")
    run_example_with_direct_config()

    ***REMOVED*** Run example with setup_movie_storage utility
    print("\n3. Example using setup_movie_storage utility:")
    setup_movie_storage(log_dir=Path("./logs"), log_level="INFO", verbose=True)

    print("\nAll examples completed. Check the logs directory for log files.")


if __name__ == "__main__":
    main()
