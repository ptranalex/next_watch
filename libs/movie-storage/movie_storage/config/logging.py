"""Logging configuration for movie storage."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from movie_storage.config.app import Config

***REMOVED*** Logger for this module
logger = logging.getLogger(__name__)


def configure_logging(
    config: Optional[Config] = None,
    log_dir: Optional[Path] = None,
    log_level: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """Configure logging for the movie storage module.

    Args:
        config: Config instance (if None, will create one)
        log_dir: Directory for log files (optional)
        log_level: Log level override (optional)
        verbose: Whether to enable verbose logging
        quiet: Whether to suppress most logging

    Returns:
        Dictionary with logging information
    """
    ***REMOVED*** Get config instance if not provided
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Determine log level
    if verbose:
        console_level = logging.DEBUG
    elif quiet:
        console_level = logging.WARNING
    else:
        console_level = getattr(logging, log_level or config.log_level, logging.INFO)

    ***REMOVED*** Get SQL log level
    sql_level = getattr(logging, config.sql_log_level, logging.WARNING)

    ***REMOVED*** Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(
        logging.DEBUG
    )  ***REMOVED*** Set to lowest level, handlers filter from there

    ***REMOVED*** Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    ***REMOVED*** Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)

    ***REMOVED*** Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    ***REMOVED*** Add handler to root logger
    root_logger.addHandler(console_handler)

    ***REMOVED*** Create file handler if log_dir is provided
    file_handler = None
    if log_dir:
        try:
            ***REMOVED*** Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)

            ***REMOVED*** Create log file path
            log_file = log_dir / "movie_storage.log"

            ***REMOVED*** Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  ***REMOVED*** Log everything to file
            file_handler.setFormatter(formatter)

            ***REMOVED*** Add handler to root logger
            root_logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")

    ***REMOVED*** Configure SQLAlchemy logging
    logging.getLogger("sqlalchemy").setLevel(sql_level)
    logging.getLogger("sqlalchemy.engine").setLevel(sql_level)

    ***REMOVED*** Default SQLModel logging to WARNING to avoid excessive output
    logging.getLogger("sqlmodel").setLevel(logging.WARNING)

    logger.debug(
        f"Logging configured with console level: {logging.getLevelName(console_level)}"
    )

    return {
        "console_level": console_level,
        "sql_level": sql_level,
        "log_file": str(log_dir / "movie_storage.log") if log_dir else None,
    }
