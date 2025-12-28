"""CLI package for BFF API application.

This package provides a command-line interface for the BFF API service,
implemented using Typer. It includes commands for server management,
health checks, cache operations, and configuration display.

The CLI is designed to follow best practices for Python command-line tools:
- Logical command grouping
- Comprehensive help text
- Type-safe interfaces
- Rich console output
- Proper error handling and exit codes

For usage information, run:
    python -m bff_api.cli.main --help

See the README.md file in this directory for detailed documentation.
"""

from . import utils
from .main import app, main

__all__ = ["main", "app", "utils"]
