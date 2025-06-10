"""Logging configuration for the Authentication API."""

from pathlib import Path
from auth_api.config.logging import configure_logging
from auth_api.config.app import settings


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    ***REMOVED*** Use the comprehensive logging configuration from config module
    log_dir = Path(settings.log_dir) if settings.log_dir else None
    configure_logging(
        log_level=settings.log_level,
        log_dir=log_dir,
        verbose=settings.debug,
        quiet=False,
    )
