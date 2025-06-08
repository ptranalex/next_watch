"""Logging configuration wrapper for the Backend API service.

This module provides a clean interface to the comprehensive logging
configuration in the config module.
"""

import logging
from pathlib import Path
from typing import Optional

from backend_api.config.logging import configure_logging as _configure_logging
from backend_api.config.app import settings

logger = logging.getLogger(__name__)


def setup_logging(
    log_level: Optional[str] = None,
    verbose: Optional[bool] = None,
    quiet: bool = False,
) -> None:
    """Setup logging for the application.

    This is a convenience wrapper around the comprehensive logging
    configuration in the config module.

    Args:
        log_level: Override the log level from settings
        verbose: Override the verbose setting from settings.debug
        quiet: Whether to suppress console output
    """
    ***REMOVED*** Use settings defaults if not provided
    if log_level is None:
        log_level = settings.log_level
    if verbose is None:
        verbose = settings.debug

    ***REMOVED*** Determine log directory
    log_dir = None
    if hasattr(settings, "log_dir") and settings.log_dir:
        log_dir = Path(settings.log_dir)

    ***REMOVED*** Configure logging using the comprehensive config module
    _configure_logging(
        log_level=log_level,
        log_dir=log_dir,
        verbose=verbose,
        quiet=quiet,
    )

    logger.info("Logging configuration initialized via core module")
