"""Configuration package for the bff_api module.

This package provides centralized configuration for the application using the simplified
NextWatch configuration library.
"""

from .app import (
    BFFAPIConfig,
    get_cache_settings,
    settings,
)

# Backward compatibility: Import old Config class name
Config = BFFAPIConfig

__all__ = [
    # Configuration classes and functions
    "BFFAPIConfig",
    "Config",  # Backward compatibility alias
    "settings",
    "get_cache_settings",
]
