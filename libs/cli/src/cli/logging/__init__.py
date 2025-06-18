"""CLI-specific logging framework.

Provides enterprise-grade logging configuration and utilities for CLI applications,
following the proven patterns from BFF API CLI with structured logging and proper
separation between user output and operational logging.
"""

from .setup import configure_cli_logging, get_logger
from .structured import CLILogger, with_logging
from .formatters import COLOR_THEMES

__all__ = [
    "configure_cli_logging",
    "get_logger",
    "CLILogger",
    "with_logging",
    "COLOR_THEMES",
]
