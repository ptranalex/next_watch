"""Backend API CLI module."""

import logging
import sys
import typer
from rich.console import Console
from rich.traceback import install

***REMOVED*** Import commands (to be added as we create them)
from backend_api.cli.commands import redis

***REMOVED*** Import app configuration and logging
from backend_api.config.app import settings

***REMOVED*** Install rich traceback handler
install()

***REMOVED*** Initialize Typer app
app = typer.Typer(
    name="backend-api",
    help="Backend API administration tools.",
    add_completion=False,
)

***REMOVED*** Configure logging
logger = logging.getLogger("backend_api.cli")

***REMOVED*** Add command groups
app.add_typer(redis.app, name="redis")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        sys.exit(1)


__all__ = ["app", "main"]
