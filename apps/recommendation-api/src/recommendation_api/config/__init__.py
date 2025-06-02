"""Configuration module for the Recommendation API.

This module provides centralized configuration management for the Recommendation API,
including environment variables, logging settings, and application settings.
"""

from recommendation_api.config.app import Config, settings
from recommendation_api.config.logging import configure_logging, get_logger

__all__ = [
    "Config",
    "settings",
    "configure_logging",
    "get_logger",
] 