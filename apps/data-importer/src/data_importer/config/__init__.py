"""Configuration package for the data_importer module.

This package provides centralized configuration for the application,
including app settings, logging configuration, and environment variable handling.
"""

from .app import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGS_DIR,
    DEFAULT_QUIET,
    DEFAULT_VERBOSE,
    Config,
)
from .env import (
    find_project_root,
    get_env_bool,
    get_env_int,
    get_env_var,
    load_environment_variables,
)
from .logging import configure_logging, with_logging

__all__ = [
    "Config",
    "configure_logging",
    "with_logging",
    "DEFAULT_LOGS_DIR",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_VERBOSE",
    "DEFAULT_QUIET",
    # Environment utilities
    "get_env_var",
    "get_env_bool",
    "get_env_int",
    "load_environment_variables",
    "find_project_root",
]
