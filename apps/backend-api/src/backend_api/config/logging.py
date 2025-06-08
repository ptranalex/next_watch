"""Centralized logging configuration for the backend API.

This module provides configuration for application-wide logging, ensuring
consistent log formatting, file output, and console display based on verbosity settings.

Best Practice: Use configure_logging() explicitly in your main/startup code rather than
decorators that have hidden side effects.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def configure_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files (if None, only console logging)
        verbose: Whether to show verbose output in console
        quiet: Whether to suppress all console output except errors

    Returns:
        Dictionary containing logging configuration details

    Example:
        >>> from pathlib import Path
        >>> config = configure_logging(
        ...     log_level="DEBUG",
        ...     log_dir=Path("./logs"),
        ...     verbose=True
        ... )
        >>> logger = logging.getLogger("backend_api")
        >>> logger.info("Application started")
    """
    ***REMOVED*** Convert log_level to uppercase to ensure compatibility with logging module
    log_level = log_level.upper()

    root_logger = logging.getLogger("backend_api")
    root_logger.setLevel(log_level)
    root_logger.handlers = []  ***REMOVED*** Clear any existing handlers

    ***REMOVED*** Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    config_info: Dict[str, Any] = {
        "log_level": log_level,
        "verbose": verbose,
        "quiet": quiet,
        "log_file": None,
        "handlers": [],
    }

    ***REMOVED*** Add file handler if log_dir is provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"backend_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        config_info["log_file"] = str(log_file)
        config_info["handlers"].append("file")
        root_logger.debug(f"Log file: {log_file}")

    ***REMOVED*** Add console handler based on verbosity
    if not quiet:
        console_level = logging.DEBUG if verbose else logging.INFO
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_level)
        root_logger.addHandler(console_handler)
        config_info["handlers"].append("console")

    ***REMOVED*** Always log errors to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setFormatter(console_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    config_info["handlers"].append("error")

    ***REMOVED*** Suppress logs from external libraries unless in verbose mode
    if not verbose:
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("alembic").setLevel(logging.WARNING)

    ***REMOVED*** Log initial configuration
    root_logger.debug(f"Logging configured: level={log_level}, verbose={verbose}, quiet={quiet}")

    return config_info


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("This is a log message")
    """
    return logging.getLogger(f"backend_api.{name}")
