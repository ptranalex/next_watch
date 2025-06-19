"""Configuration package for the bff_api module.

This package provides centralized configuration for the application using the simplified
NextWatch configuration library.
"""

from .app import (
    BFFAPIConfig,
    get_settings,
    settings,
)

***REMOVED*** Backward compatibility: Import old Config class name
Config = BFFAPIConfig

__all__ = [
    ***REMOVED*** Configuration classes and functions
    "BFFAPIConfig",
    "Config",  ***REMOVED*** Backward compatibility alias
    "get_settings",
    "settings",
]
