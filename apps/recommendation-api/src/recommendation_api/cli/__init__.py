"""CLI package for the Recommendation API.

This package provides command-line interface tools for managing the Recommendation API,
including server management, configuration, health checks, and embedding operations.
"""

import importlib.metadata
from typing import Optional

***REMOVED*** Try to get version from package metadata
try:
    __version__ = importlib.metadata.version("recommendation-api")
except (importlib.metadata.PackageNotFoundError, AttributeError):
    __version__ = "development"

***REMOVED*** Expose main CLI app
from recommendation_api.cli.main import app as cli_app

***REMOVED*** Expose utility functions
from recommendation_api.cli.utils import (
    print_error,
    print_success,
    print_config,
)

***REMOVED*** Expose command modules
from recommendation_api.cli.commands import (
    serve,
    config,
    health,
    embeddings,
    debug,
)

__all__ = [
    ***REMOVED*** Version
    "__version__",
    
    ***REMOVED*** Main CLI app
    "cli_app",
    
    ***REMOVED*** Utility functions
    "print_error",
    "print_success",
    "print_config",
    
    ***REMOVED*** Command modules
    "serve",
    "config",
    "health",
    "embeddings",
    "debug",
] 