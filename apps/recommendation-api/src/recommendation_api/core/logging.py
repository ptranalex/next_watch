"""Logging configuration for the Recommendation API."""

from recommendation_api.config.logging import configure_logging
from recommendation_api.config import settings


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    ***REMOVED*** Use the comprehensive logging configuration from config module
    configure_logging(log_level=settings.log_level.upper(), verbose=settings.debug, quiet=False)
