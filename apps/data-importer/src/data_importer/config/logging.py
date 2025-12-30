"""Centralized logging configuration for the data importer.

This module provides configuration for application-wide logging, ensuring
consistent log formatting, file output, and console display based on verbosity settings.
"""

import functools
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

# Type variable for function decoration
F = TypeVar("F", bound=Callable[..., Any])


def configure_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files (if None, only console logging)
        verbose: Whether to show verbose output in console
        quiet: Whether to suppress all console output except errors
    """
    root_logger = logging.getLogger("data_importer")
    root_logger.setLevel(log_level)
    root_logger.handlers = []  # Clear any existing handlers

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    # Add file handler if log_dir is provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"data_importer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        root_logger.debug(f"Log file: {log_file}")

    # Add console handler based on verbosity
    if not quiet:
        console_level = logging.DEBUG if verbose else logging.INFO
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_level)
        root_logger.addHandler(console_handler)

    # Always log errors to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setFormatter(console_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Suppress logs from external libraries unless in verbose mode
    if not verbose:
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    # Log initial configuration
    root_logger.debug(f"Logging configured: level={log_level}, verbose={verbose}, quiet={quiet}")


def with_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to configure logging for a function.

    This decorator applies the configure_logging function before
    executing the decorated function. It can be used to easily
    add logging configuration to any function or method.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files (if None, only console logging)
        verbose: Whether to show verbose output in console
        quiet: Whether to suppress all console output except errors

    Returns:
        Decorator function

    Examples:
        Decorate a simple function with default logging config:

        >>> @with_logging()
        >>> def my_function():
        >>>     logger = logging.getLogger(__name__)
        >>>     logger.info("This will be logged")
        >>>     return "result"

        Decorate an async function with custom logging config:

        >>> @with_logging(log_level="DEBUG", log_dir=Path("./logs"), verbose=True)
        >>> async def my_async_function(arg1, arg2):
        >>>     logger = logging.getLogger(__name__)
        >>>     logger.debug(f"Processing {arg1} and {arg2}")
        >>>     return await process_data(arg1, arg2)

        Decorate a main CLI entry point:

        >>> @with_logging(log_level="INFO", log_dir=DEFAULT_LOGS_DIR)
        >>> def main():
        >>>     logger = logging.getLogger(__name__)
        >>>     logger.info("Starting application")
        >>>     # Run the application
        >>>     app.run()
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Configure logging before executing the function
            configure_logging(log_level=log_level, log_dir=log_dir, verbose=verbose, quiet=quiet)

            # Call the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
