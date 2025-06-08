"""CLI package for the Recommendation API.

This package provides command-line interface tools for managing the Recommendation API,
including server management, configuration, health checks, and embedding operations.
"""

import importlib.metadata
import logging
import sys
from typing import Optional

***REMOVED*** Try to get version from package metadata
try:
    __version__ = importlib.metadata.version("recommendation_api")
except (importlib.metadata.PackageNotFoundError, AttributeError):
    __version__ = "development"


***REMOVED*** Entry point for hatch to call
def main() -> None:
    """Main entry point for CLI when called via `rec-api` command."""
    try:
        ***REMOVED*** Import here to avoid circular imports
        from recommendation_api.cli.main import app as cli_app

        cli_app()
    except Exception as e:
        ***REMOVED*** Simple error handling if logging is not yet set up
        logger = logging.getLogger("recommendation_api.cli")
        logger.error(f"Error running command: {str(e)}")

        ***REMOVED*** Use rich for prettier output if available
        try:
            from rich.console import Console

            console = Console()
            console.print(f"[bold red]CLI Error: {e}[/bold red]")
        except ImportError:
            print(f"CLI Error: {e}", file=sys.stderr)

        sys.exit(1)


***REMOVED*** Import these after the main function to avoid circular imports
from recommendation_api.cli.main import app as cli_app
from recommendation_api.cli.utils import (
    print_error,
    print_success,
    print_config,
)

***REMOVED*** Import command modules - these are primarily for IDE auto-completion and docs
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
    ***REMOVED*** Main function
    "main",
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
