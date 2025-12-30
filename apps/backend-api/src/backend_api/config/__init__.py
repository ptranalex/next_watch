"""Configuration package for the Backend API service.

This package provides configuration using the shared NextWatch configuration
library with type-safe validation and production-ready defaults.
"""

# Main configuration class and global settings instance
from backend_api.config.app import BackendAPIConfig, settings

# Backward compatible alias
Config = BackendAPIConfig

# Note: Logging utilities now available from shared config library:
# from config.logging import configure_logging, get_logger

# Export configuration utilities
__all__ = [
    "Config",  # Main configuration class (alias for BackendAPIConfig)
    "BackendAPIConfig",  # Original class name for explicit imports
    "settings",  # Global settings instance
    # Logging utilities now available from shared config library:
    # "configure_logging",  # Use: from config.logging import configure_logging
    # "get_logger",         # Use: from config.logging import get_logger
]
