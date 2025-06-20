"""Configuration module for the Recommendation API.

This module provides centralized configuration management for the Recommendation API,
including environment variables, logging settings, and application settings.
"""

from recommendation_api.config.app import RecommendationAPIConfig, settings
from config.logging import get_logger, configure_logging

***REMOVED*** Backward compatibility: Import old Config class name
Config = RecommendationAPIConfig

__all__ = [
    "RecommendationAPIConfig",
    "Config",  ***REMOVED*** Backward compatibility alias
    "settings",
    "configure_logging",
    "get_logger",
]
