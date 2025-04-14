"""Centralized logging configuration for the ebook summarizer.

This module provides configuration for application-wide logging, ensuring
consistent log formatting, file output, and console display based on verbosity settings.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


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
    root_logger = logging.getLogger("ha_assistant")
    root_logger.setLevel(log_level)
    root_logger.handlers = []  ***REMOVED*** Clear any existing handlers

    ***REMOVED*** Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    ***REMOVED*** Add file handler if log_dir is provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = (
            log_dir / f"ha_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        root_logger.debug(f"Log file: {log_file}")

    ***REMOVED*** Add console handler based on verbosity
    if not quiet:
        console_level = logging.DEBUG if verbose else logging.INFO
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_level)
        root_logger.addHandler(console_handler)

    ***REMOVED*** Always log errors to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setFormatter(console_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    ***REMOVED*** Suppress logs from external libraries unless in verbose mode
    if not verbose:
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    ***REMOVED*** Log initial configuration
    root_logger.debug(
        f"Logging configured: level={log_level}, verbose={verbose}, quiet={quiet}"
    )
