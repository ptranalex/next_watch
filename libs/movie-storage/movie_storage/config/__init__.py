"""Configuration package for movie storage."""

from movie_storage.config.app import Config, ConfigDict
from movie_storage.config.env import (
    find_project_root,
    get_env_bool,
    get_env_int,
    get_env_var,
    load_environment_variables,
)
from movie_storage.config.logging import configure_logging, with_logging

# Export all configuration utilities
__all__ = [
    # Core configuration
    "Config",
    "ConfigDict",
    # Environment utilities
    "get_env_var",
    "get_env_bool",
    "get_env_int",
    "load_environment_variables",
    "find_project_root",
    # Logging utilities
    "configure_logging",
    "with_logging",
]
