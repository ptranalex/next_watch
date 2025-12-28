"""Main CLI application for Recommendation API service."""

import importlib.metadata
import logging
import sys

import typer
from rich.console import Console
from rich.traceback import install

***REMOVED*** Import command modules
from recommendation_api.cli.commands import cache, config, debug, embeddings, health, ml, serve

***REMOVED*** Import configuration and utilities
from recommendation_api.config.app import settings

***REMOVED*** Install rich traceback handler
install()

console = Console()
logger = logging.getLogger(__name__)

***REMOVED*** Create main Typer app
app = typer.Typer(
    name="rec-api",
    help="Recommendation API service for Next Watch movie platform",
    add_completion=False,
)

***REMOVED*** Add command groups
app.add_typer(serve.app, name="serve")
app.add_typer(config.app, name="config")
app.add_typer(health.app, name="health")
app.add_typer(embeddings.app, name="embeddings")
app.add_typer(debug.app, name="debug")
app.add_typer(ml.app, name="ml")
app.add_typer(cache.app, name="cache")


@app.command(name="version")
def show_version() -> None:
    """Show Recommendation API version information."""
    try:
        ***REMOVED*** Try to get version from package metadata
        try:
            version = importlib.metadata.version("recommendation_api")
        except (importlib.metadata.PackageNotFoundError, AttributeError):
            version = "development"

        console.print(f"[bold blue]Recommendation API[/bold blue] version [green]{version}[/green]")
        console.print(f"Environment: [yellow]{settings.environment}[/yellow]")
        console.print(f"Python: [dim]{sys.version.split()[0]}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error getting version: {e}[/bold red]")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
