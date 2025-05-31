"""Main CLI application for BFF service."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import typer
import uvicorn
from rich.console import Console
from rich.traceback import install

***REMOVED*** Import command modules
from bff_api.cli.commands import health, cache

***REMOVED*** Import configuration and utilities
from bff_api.config.app import settings, Config
from bff_api.cli.utils import print_config
from bff_api.main import create_app

***REMOVED*** Install rich traceback handler
install()

console = Console()
logger = logging.getLogger(__name__)

***REMOVED*** Create main Typer app
app = typer.Typer(
    name="bff-api",
    help="Backend for Frontend API service for Next Watch movie platform",
    add_completion=False,
)

***REMOVED*** Add command groups
app.add_typer(health.app, name="health")
app.add_typer(cache.app, name="cache")


@app.command()
def serve(
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        help="Host to bind server to",
        envvar="HOST",
    ),
    port: int = typer.Option(
        None,
        "--port",
        "-p",
        help="Port to bind server to",
        envvar="PORT",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
    log_level: str = typer.Option(
        None,
        "--log-level",
        help="Set log level (DEBUG, INFO, WARNING, ERROR)",
        envvar="LOG_LEVEL",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging and output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress console output except errors",
    ),
) -> None:
    """Start the BFF API server.

    Args:
        host: Host address to bind the server to
        port: Port number to bind the server to
        reload: Whether to enable auto-reload for development
        log_level: Logging level for the application
        verbose: Enable verbose console output
        quiet: Suppress console output except errors
    """
    try:
        ***REMOVED*** Create configuration with CLI overrides
        config_kwargs: Dict[str, Any] = {}
        if host:
            config_kwargs["host"] = host
        if port:
            config_kwargs["port"] = port
        if log_level:
            config_kwargs["log_level"] = log_level.upper()

        ***REMOVED*** Update global settings if any CLI overrides are provided
        if config_kwargs:
            config = Config(**config_kwargs)
        else:
            config = settings

        ***REMOVED*** Display configuration unless quiet mode
        if not quiet:
            if verbose:
                print_config(config, "BFF Server Configuration", console)
            else:
                console.print(f"[blue]Starting BFF API server on {config.host}:{config.port}[/blue]")
                console.print(f"[dim]Environment: {config.environment} | Debug: {config.debug}[/dim]")

        ***REMOVED*** Configure logging level
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        elif quiet:
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=getattr(logging, config.log_level))

        logger.info(f"Starting BFF API server on {config.host}:{config.port}")

        if verbose:
            logger.debug(f"Configuration: host={config.host}, port={config.port}, reload={reload}")

        ***REMOVED*** Start server
        if reload:
            ***REMOVED*** Use import string for reload mode
            uvicorn.run(
                "bff_api.main:app",
                host=config.host,
                port=config.port,
                reload=reload,
                log_level=config.log_level.lower(),
                access_log=not config.is_production,
            )
        else:
            ***REMOVED*** Use app instance for production mode (more efficient)
            fastapi_app = create_app()
            uvicorn.run(
                fastapi_app,
                host=config.host,
                port=config.port,
                reload=reload,
                log_level=config.log_level.lower(),
                access_log=not config.is_production,
            )

    except Exception as e:
        console.print(f"[bold red]Error starting server: {e}[/bold red]")
        logger.error(f"Failed to start server: {e}")
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
            console.print(f"[dim]Configuration loaded from: {settings.environment} environment[/dim]")
            console.print(f"[dim]Debug mode: {'Enabled' if settings.debug else 'Disabled'}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error displaying configuration: {e}[/bold red]")
        logger.error(f"Failed to display configuration: {e}")
        raise typer.Exit(code=1)


@app.command(name="version")
def show_version() -> None:
    """Show BFF API version information."""
    try:
        ***REMOVED*** Try to get version from package metadata
        try:
            import importlib.metadata
            version = importlib.metadata.version("bff-api")
        except (importlib.metadata.PackageNotFoundError, AttributeError):
            version = "development"

        console.print(f"[bold blue]BFF API[/bold blue] version [green]{version}[/green]")
        console.print(f"Environment: [yellow]{settings.environment}[/yellow]")
        console.print(f"Python: [dim]{sys.version.split()[0]}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error getting version: {e}[/bold red]")
        raise typer.Exit(code=1)


def main() -> None:
    """Main entry point for CLI."""
    try:
        app()
    except Exception as e:
        ***REMOVED*** Use basic logging since configure_logging might not be set up yet
        logger = logging.getLogger("bff_api.cli")
        logger.error(f"Error running command: {str(e)}")
        console.print(f"[bold red]CLI Error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
