"""Configuration module for the Recommendation API.

This module provides centralized configuration management for the Recommendation API,
including environment variables, logging settings, and application settings.
"""

from config.logging import configure_logging, get_logger

from recommendation_api.config.app import RecommendationAPIConfig, settings

***REMOVED*** Backward compatibility: Import old Config class name
Config = RecommendationAPIConfig

__all__ = [
    "RecommendationAPIConfig",
    "Config",  ***REMOVED*** Backward compatibility alias
    "settings",
    "configure_logging",
    "get_logger",
]
