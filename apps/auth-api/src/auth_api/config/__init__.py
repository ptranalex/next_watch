"""Configuration package for the auth_api module.

This package provides centralized configuration for the application,
including app settings.
"""

from .app import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_DATABASE_URL,
    DEFAULT_API_PORT,
    DEFAULT_CORS_ORIGINS,
    DEFAULT_DEBUG,
    DEFAULT_ENABLE_PERFORMANCE_METRICS,
    Config,
)

__all__ = [
    "Config",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_DATABASE_URL",
    "DEFAULT_API_PORT",
    "DEFAULT_CORS_ORIGINS",
    "DEFAULT_DEBUG",
    "DEFAULT_ENABLE_PERFORMANCE_METRICS",
]
