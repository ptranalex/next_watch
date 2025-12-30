"""Logging configuration for movie storage."""

import functools
import logging
import os
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from movie_storage.config.app import Config

# Logger for this module
logger = logging.getLogger(__name__)


def configure_logging(
    config: Config | None = None,
    log_dir: Path | None = None,
    log_level: str | None = None,
    verbose: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
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
    # Get config instance if not provided
    if config is None:
        config = Config.get_instance()

    # Determine log level
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

    # Get SQL log level
    sql_level = getattr(logging, config.sql_log_level.upper(), logging.WARNING)

    # Configure root logger for movie_storage
    root_logger = logging.getLogger("movie_storage")
    root_logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers filter from there
    root_logger.propagate = False

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    # Create console handler for standard output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Always add error handler to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_handler)

    # Create file handler if log_dir is provided
    log_file_path = None
    if log_dir:
        try:
            # Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)

            # Create log file path with timestamp
            log_file_path = (
                log_dir / f"movie_storage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )

            # Create file handler
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            file_handler.setFormatter(file_formatter)

            # Add handler to root logger
            root_logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_file_path}")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")

    # Configure SQLAlchemy logging
    logging.getLogger("sqlalchemy").setLevel(sql_level)
    logging.getLogger("sqlalchemy.engine").setLevel(sql_level)

    # Default SQLModel logging to WARNING to avoid excessive output
    logging.getLogger("sqlmodel").setLevel(logging.WARNING)

    # Log initial configuration
    logger.debug(
        f"Logging configured: level={logging.getLevelName(level_value)}, verbose={verbose}, quiet={quiet}"
    )

    return {
        "console_level": console_level,
        "sql_level": sql_level,
        "log_file": str(log_file_path) if log_file_path else None,
    }


def with_logging(
    log_level: str | None = None,
    log_dir: Path | None = None,
    verbose: bool = False,
    quiet: bool = False,
    config: Config | None = None,
) -> Callable[[Callable], Callable]:
    """Decorator to configure logging for a function.

    This decorator applies the configure_logging function before
    executing the decorated function. It can be used to easily
    add logging configuration to any function or method.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files (if None, only console logging)
        verbose: Whether to show verbose output in console
        quiet: Whether to suppress all console output except errors
        config: Config instance for database settings

    Returns:
        Decorator function

    Examples:
        Decorate a simple function with default logging config:

        >>> @with_logging()
        >>> def my_function():
        >>>     logger = logging.getLogger(__name__)
        >>>     logger.info("This will be logged")
        >>>     return "result"

        Decorate a function with custom logging config:

        >>> @with_logging(log_level="DEBUG", log_dir=Path("./logs"), verbose=True)
        >>> def my_function(arg1, arg2):
        >>>     logger = logging.getLogger(__name__)
        >>>     logger.debug(f"Processing {arg1} and {arg2}")
        >>>     return process_data(arg1, arg2)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Configure logging before executing the function
            configure_logging(
                log_level=log_level,
                log_dir=log_dir,
                verbose=verbose,
                quiet=quiet,
                config=config,
            )

            # Call the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
