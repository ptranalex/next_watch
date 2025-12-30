"""Configuration package for the Authentication API service.

This package provides configuration using the shared NextWatch configuration
library with type-safe validation and production-ready defaults.
"""

# Main configuration class and global settings instance
from auth_api.config.app import AuthAPIConfig, settings

# Create alias for backward compatibility
Config = AuthAPIConfig

# Note: Logging utilities now available from shared config library:
# from config.logging import configure_logging, get_logger

# Export configuration utilities
__all__ = [
    "Config",  # Main configuration class (alias for AuthAPIConfig)
    "AuthAPIConfig",  # Original class name for explicit imports
    "settings",  # Global settings instance
    # Logging utilities now available from shared config library:
    # "configure_logging",  # Use: from config.logging import configure_logging
    # "get_logger",         # Use: from config.logging import get_logger
]
