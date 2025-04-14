"""Configuration package for the Home Assistant Assistant.

This package provides centralized configuration for the application,
including app settings and logging configuration.
"""

from .app import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGS_DIR,
    DEFAULT_QUIET,
    DEFAULT_VERBOSE,
    Config,
)
from .logging import configure_logging

__all__ = [
    "Config",
    "configure_logging",
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_LOGS_DIR",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_VERBOSE",
    "DEFAULT_QUIET",
    "DEFAULT_CACHE_TTL",
]
