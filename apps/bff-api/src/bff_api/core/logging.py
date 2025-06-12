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
    color_theme: str = "modern",
) -> None:
    """Setup structured logging for the BFF application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        verbose: Enable verbose logging (uses debug mode if None)
        quiet: Disable console output
        color_theme: Color theme for console output (modern, classic, minimal, solarized)
    """
    ***REMOVED*** Use settings defaults if not provided
    if log_level is None:
        log_level = settings.log_level
    if verbose is None:
        verbose = settings.debug

    ***REMOVED*** Determine log directory from settings
    log_dir = None
    if hasattr(settings, "logs_dir") and settings.logs_dir:
        log_dir = Path(settings.logs_dir)

    ***REMOVED*** Configure using comprehensive config module with structlog
    _configure_logging(
        log_level=log_level,
        log_dir=log_dir,
        verbose=verbose,
        quiet=quiet,
        use_coloredlogs=True,  ***REMOVED*** Enable colored output
        logger_name="bff_api",  ***REMOVED*** Set the logger name
        color_theme=color_theme,  ***REMOVED*** Apply color theme
    )
