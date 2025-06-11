"""Logging configuration for movie storage."""

import functools
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from backend_api.config.app import Config

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
    if log_level:
        level_value = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level_value = getattr(logging, config.log_level.upper(), logging.INFO)

    if verbose:
        console_level = logging.DEBUG
    elif quiet:
        console_level = logging.WARNING
    else:
        console_level = level_value

    ***REMOVED*** Get SQL log level
    sql_level = getattr(logging, config.sql_log_level.upper(), logging.WARNING)

    ***REMOVED*** Configure root logger for backend_api
    root_logger = logging.getLogger("backend_api")
    root_logger.setLevel(logging.DEBUG)  ***REMOVED*** Set to lowest level, handlers filter from there
    root_logger.propagate = False

    ***REMOVED*** Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    ***REMOVED*** Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    ***REMOVED*** Create console handler for standard output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    ***REMOVED*** Always add error handler to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_handler)

    ***REMOVED*** Create file handler if log_dir is provided
    log_file_path = None
    if log_dir:
        try:
            ***REMOVED*** Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)

            ***REMOVED*** Create log file path with timestamp
            log_file_path = log_dir / f"backend_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            ***REMOVED*** Create file handler
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)  ***REMOVED*** Log everything to file
            file_handler.setFormatter(file_formatter)

            ***REMOVED*** Add handler to root logger
            root_logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_file_path}")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")

    ***REMOVED*** Configure SQLAlchemy logging
    logging.getLogger("sqlalchemy").setLevel(sql_level)
    logging.getLogger("sqlalchemy.engine").setLevel(sql_level)

    ***REMOVED*** Default SQLModel logging to WARNING to avoid excessive output
    logging.getLogger("sqlmodel").setLevel(logging.WARNING)

    ***REMOVED*** Log initial configuration
    logger.debug(
        f"Logging configured: level={logging.getLevelName(level_value)}, verbose={verbose}, quiet={quiet}"
    )

    return {
        "console_level": console_level,
        "sql_level": sql_level,
        "log_file": str(log_file_path) if log_file_path else None,
    }


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello world")
    """
    return logging.getLogger(name)
