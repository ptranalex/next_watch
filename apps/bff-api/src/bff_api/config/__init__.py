"""Configuration package for the bff_api module.

This package provides centralized configuration for the application,
including environment variable loading and app settings.
"""

from .env import (
    get_env_var,
    get_env_bool,
    get_env_int,
    load_environment_variables,
    find_project_root,
)
from .app import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGS_DIR,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_CORS_ORIGINS,
    DEFAULT_DEBUG,
    DEFAULT_ENABLE_PERFORMANCE_METRICS,
    DEFAULT_BACKEND_API_URL,
    DEFAULT_BACKEND_API_TIMEOUT,
    DEFAULT_RECO_API_URL,
    DEFAULT_AUTH_API_URL,
    DEFAULT_REDIS_URL,
    DEFAULT_CACHE_TTL,
    DEFAULT_JWT_SECRET,
    DEFAULT_INTERNAL_API_KEY,
    DEFAULT_ALLOWED_HOSTS,
    Config,
    ConfigDict,
    settings,
)

__all__ = [
    ***REMOVED*** Environment utilities
    "get_env_var",
    "get_env_bool",
    "get_env_int",
    "load_environment_variables",
    "find_project_root",
    ***REMOVED*** Configuration classes and types
    "Config",
    "ConfigDict",
    "settings",
    ***REMOVED*** Default values
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOGS_DIR",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_CORS_ORIGINS",
    "DEFAULT_DEBUG",
    "DEFAULT_ENABLE_PERFORMANCE_METRICS",
    "DEFAULT_BACKEND_API_URL",
    "DEFAULT_BACKEND_API_TIMEOUT",
    "DEFAULT_RECO_API_URL",
    "DEFAULT_AUTH_API_URL",
    "DEFAULT_REDIS_URL",
    "DEFAULT_CACHE_TTL",
    "DEFAULT_JWT_SECRET",
    "DEFAULT_INTERNAL_API_KEY",
    "DEFAULT_ALLOWED_HOSTS",
]
