"""Backend API CLI module."""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from typer import Typer

***REMOVED*** Import commands from their modules
from backend_api.cli.commands import cache, config, health, redis, serve, version
from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

***REMOVED*** Install rich traceback handler
install()

***REMOVED*** Initialize console
console = Console()

***REMOVED*** Initialize Typer app
app: Typer = typer.Typer(
    name="backend-api",
    help="Backend API administration tools.",
    add_completion=True,
)

***REMOVED*** Configure logging
logger = logging.getLogger("backend_api.cli")

***REMOVED*** Add command groups
app.add_typer(serve.app, name="serve")
app.add_typer(health.app, name="health")
app.add_typer(config.app, name="config")
app.add_typer(redis.app, name="redis")
app.add_typer(cache.app, name="cache")
app.add_typer(version.app, name="version")


***REMOVED*** Make serve the default command
@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Backend API CLI.

    If no command is specified, this will show the help message.
    """
    if ctx.invoked_subcommand is None:
        ***REMOVED*** Configure basic logging
        configure_logging(log_level="INFO")

        ***REMOVED*** Show help if no command is specified
        console.print("🚀 Backend API Command Line Interface")
        console.print()
        ctx.obj = {}
        typer.echo(ctx.get_help())
        sys.exit(0)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        ***REMOVED*** Use basic logging since configure_logging might not be set up yet
        logger = logging.getLogger("backend_api.cli")
        logger.error(f"Error running command: {str(e)}")
        sys.exit(1)


***REMOVED*** Support for running as a module
if __name__ == "__main__":
    main()


__all__ = ["app", "main"]
