"""Centralized logging configuration for NextWatch services.

This module provides comprehensive logging setup with structlog integration,
color themes, HTTP noise suppression, and production-ready configurations.
"""

from config.logging.setup import configure_logging, get_logger
from config.logging.themes import COLOR_THEMES

__all__ = [
    "configure_logging",
    "get_logger",
    "COLOR_THEMES",
]
