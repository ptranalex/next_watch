"""Main CLI application for BFF service."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, cast

import typer
from rich.console import Console
from rich.traceback import install
from typing_extensions import Annotated

***REMOVED*** Import command modules
from bff_api.cli.commands import health, cache, serve

***REMOVED*** Import configuration and utilities
from bff_api.config.app import settings, Config
from bff_api.cli.utils import print_config
from bff_api.main import create_app

***REMOVED*** Define version constant
DEFAULT_VERSION = "0.1.0"  ***REMOVED*** Should match pyproject.toml

***REMOVED*** Install rich traceback handler
install()

console = Console()
logger = logging.getLogger(__name__)

***REMOVED*** Create main Typer app
app: typer.Typer = typer.Typer(
    name="bff-api",
    help="Backend for Frontend API service for Next Watch movie platform",
    add_completion=False,
)

***REMOVED*** Add command groups with explicit casting for proper type checking
app.add_typer(health.app, name="health")
app.add_typer(cache.app, name="cache")
app.add_typer(serve.app, name="serve")


@app.command(name="version")
def show_version() -> None:
    """Show BFF API version information."""
    try:
        ***REMOVED*** Try to get version from package metadata
        try:
            import importlib.metadata

            version = importlib.metadata.version("bff-api")
        except (importlib.metadata.PackageNotFoundError, AttributeError):
            version = DEFAULT_VERSION

        console.print(f"[bold blue]BFF API[/bold blue] version [green]{version}[/green]")
        console.print(f"Environment: [yellow]{settings.environment}[/yellow]")
        console.print(f"Python: [dim]{sys.version.split()[0]}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error getting version: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def config(
    show_secrets: bool = typer.Option(
        False,
        "--show-secrets",
        help="Show sensitive configuration values (use with caution)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed configuration information",
    ),
) -> None:
    """Display current configuration.

    Args:
        show_secrets: Whether to show sensitive values unmasked
        verbose: Show additional configuration details
    """
    try:
        title = "BFF Configuration"
        if verbose:
            title += " (Detailed)"

        print_config(settings, title, console, show_secrets=show_secrets)

        if verbose:
            console.print(
                f"[dim]Configuration loaded from: {settings.environment} environment[/dim]"
            )
            console.print(f"[dim]Debug mode: {'Enabled' if settings.debug else 'Disabled'}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error displaying configuration: {e}[/bold red]")
        logger.error(f"Failed to display configuration: {e}")
        raise typer.Exit(code=1)


def main() -> int:
    """Main entry point for CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        app()
        return 0
    except Exception as e:
        ***REMOVED*** Use basic logging since configure_logging might not be set up yet
        logger = logging.getLogger("bff_api.cli")
        logger.error(f"Error running command: {str(e)}")
        console.print(f"[bold red]CLI Error: {e}[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
