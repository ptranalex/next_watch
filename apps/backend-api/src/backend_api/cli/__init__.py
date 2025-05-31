"""Backend API CLI module."""

import logging
import sys
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.traceback import install

***REMOVED*** Import commands (to be added as we create them)
from backend_api.cli.commands import redis

***REMOVED*** Import app configuration and logging
from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

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


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(
        getattr(settings, "api_port", 8000), help="Port to bind to"
    ),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
    log_level: str = typer.Option(
        "info", help="Log level (debug, info, warning, error)"
    ),
    log_dir: Optional[str] = typer.Option(None, help="Directory for log files"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress console output except errors"
    ),
):
    """Start the backend API server.

    Args:
        host: Host address to bind the server to
        port: Port number to bind the server to
        reload: Whether to enable auto-reload for development
        log_level: Logging level for the application
        log_dir: Directory to store log files (optional)
        verbose: Enable verbose console output
        quiet: Suppress console output except errors
    """
    import uvicorn

    ***REMOVED*** Configure logging
    configure_logging(
        log_level=log_level.upper(),
        log_dir=Path(log_dir) if log_dir else None,
        verbose=verbose,
        quiet=quiet,
    )

    logger = get_logger(__name__)
    logger.info(f"Starting Next Watch Backend API on {host}:{port}")

    if verbose:
        logger.debug(f"Configuration: host={host}, port={port}, reload={reload}")

    uvicorn.run(
        "backend_api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.command()
def health(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Check the health of the backend API service.

    Args:
        verbose: Show detailed output including response data
    """
    import httpx

    ***REMOVED*** Configure minimal logging for health check
    configure_logging(log_level="ERROR", quiet=not verbose)
    logger = get_logger(__name__)

    port = getattr(settings, "api_port", 8000)
    url = f"http://localhost:{port}/health"

    try:
        if verbose:
            typer.echo(f"🔍 Checking backend API health at {url}")

        response = httpx.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        typer.echo(f"✅ Backend API is healthy: {data}")

        if verbose:
            logger.info(f"Health check successful: {data}")

    except httpx.RequestError as e:
        error_msg = f"❌ Failed to connect to backend API: {e}"
        typer.echo(error_msg)
        logger.error(error_msg)
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        error_msg = f"❌ Backend API returned error: {e}"
        typer.echo(error_msg)
        logger.error(error_msg)
        raise typer.Exit(1)


@app.command()
def config(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed configuration"
    ),
):
    """Display current configuration.

    Args:
        verbose: Show detailed configuration including sensitive information masked
    """
    configure_logging(log_level="INFO", quiet=not verbose)
    logger = get_logger(__name__)

    typer.echo("🔧 Next Watch Backend API Configuration")
    typer.echo(f"Environment: {getattr(settings, 'environment', 'unknown')}")
    typer.echo(f"Debug mode: {settings.debug}")
    typer.echo(f"API port: {getattr(settings, 'api_port', 8000)}")
    typer.echo(f"Log level: {getattr(settings, 'log_level', 'INFO')}")

    if verbose:
        typer.echo(f"Full configuration: {settings}")
        logger.info("Configuration displayed")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        ***REMOVED*** Use basic logging since configure_logging might not be set up yet
        logger = logging.getLogger("backend_api.cli")
        logger.error(f"Error running command: {str(e)}")
        sys.exit(1)


__all__ = ["app", "main"]
