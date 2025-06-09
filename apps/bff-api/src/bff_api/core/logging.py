"""Logging configuration for the BFF core module.

This module provides a clean interface to the comprehensive logging
configuration in the config module.
"""

import logging
from pathlib import Path
from typing import Optional

from bff_api.config.app import settings
from bff_api.config.logging import configure_logging as _configure_logging


def setup_logging(
    log_level: Optional[str] = None,
    verbose: Optional[bool] = None,
    quiet: bool = False,
) -> None:
    """Setup logging for the BFF application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        verbose: Enable verbose logging (uses debug mode if None)
        quiet: Disable console output
    """
    ***REMOVED*** Use settings defaults if not provided
    if log_level is None:
        log_level = settings.log_level
    if verbose is None:
        verbose = settings.debug

    ***REMOVED*** Determine log directory from settings
    log_dir = None
    if hasattr(settings, "log_dir") and settings.log_dir:
        log_dir = Path(settings.log_dir)

    ***REMOVED*** Configure using comprehensive config module
    _configure_logging(
        log_level=log_level,
        log_dir=log_dir,
        verbose=verbose,
        quiet=quiet,
    )
