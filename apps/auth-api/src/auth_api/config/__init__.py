"""Configuration package for the Authentication API service.

This package provides configuration using the shared NextWatch configuration
library with type-safe validation and production-ready defaults.
"""

***REMOVED*** Main configuration class and global settings instance
from auth_api.config.app import AuthAPIConfig, settings

***REMOVED*** Create alias for backward compatibility
Config = AuthAPIConfig

***REMOVED*** Note: Logging utilities now available from shared config library:
***REMOVED*** from config.logging import configure_logging, get_logger

***REMOVED*** Export configuration utilities
__all__ = [
    "Config",  ***REMOVED*** Main configuration class (alias for AuthAPIConfig)
    "AuthAPIConfig",  ***REMOVED*** Original class name for explicit imports
    "settings",  ***REMOVED*** Global settings instance
    ***REMOVED*** Logging utilities now available from shared config library:
    ***REMOVED*** "configure_logging",  ***REMOVED*** Use: from config.logging import configure_logging
    ***REMOVED*** "get_logger",         ***REMOVED*** Use: from config.logging import get_logger
]
