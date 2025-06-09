"""Configuration package for the backend_api module.

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
    DEFAULT_API_PORT,
    DEFAULT_CORS_ORIGINS,
    DEFAULT_DATABASE_URL,
    DEFAULT_DEBUG,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGS_DIR,
    DEFAULT_ENABLE_PERFORMANCE_METRICS,
    DEFAULT_JWT_SECRET,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
    DEFAULT_JWT_JWK_ROTATION_INTERVAL,
    DEFAULT_REDIS_URL,
    DEFAULT_REDIS_MAX_CONNECTIONS,
    DEFAULT_REDIS_SOCKET_TIMEOUT,
    DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT,
    DEFAULT_REDIS_RETRY_ON_TIMEOUT,
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
    "DEFAULT_DATABASE_URL",
    "DEFAULT_API_PORT",
    "DEFAULT_CORS_ORIGINS",
    "DEFAULT_DEBUG",
    "DEFAULT_ENABLE_PERFORMANCE_METRICS",
    "DEFAULT_JWT_SECRET",
    "DEFAULT_JWT_ALGORITHM",
    "DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS",
    "DEFAULT_JWT_JWK_ROTATION_INTERVAL",
    "DEFAULT_REDIS_URL",
    "DEFAULT_REDIS_MAX_CONNECTIONS",
    "DEFAULT_REDIS_SOCKET_TIMEOUT",
    "DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT",
    "DEFAULT_REDIS_RETRY_ON_TIMEOUT",
]
