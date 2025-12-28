"""Configuration package for the Backend API service.

This package provides configuration using the shared NextWatch configuration
library with type-safe validation and production-ready defaults.
"""

***REMOVED*** Main configuration class and global settings instance
from backend_api.config.app import BackendAPIConfig, settings

***REMOVED*** Backward compatible alias
Config = BackendAPIConfig

***REMOVED*** Note: Logging utilities now available from shared config library:
***REMOVED*** from config.logging import configure_logging, get_logger

***REMOVED*** Export configuration utilities
__all__ = [
    "Config",  ***REMOVED*** Main configuration class (alias for BackendAPIConfig)
    "BackendAPIConfig",  ***REMOVED*** Original class name for explicit imports
    "settings",  ***REMOVED*** Global settings instance
    ***REMOVED*** Logging utilities now available from shared config library:
    ***REMOVED*** "configure_logging",  ***REMOVED*** Use: from config.logging import configure_logging
    ***REMOVED*** "get_logger",         ***REMOVED*** Use: from config.logging import get_logger
]
