"""Server commands for the Backend API CLI."""

import logging
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from typer import Typer

from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

app = typer.Typer(
    name="serve",
    help="Start and manage the Backend API server.",
    add_completion=False,
)

console = Console()
logger = logging.getLogger("backend_api.cli.commands.serve")


@app.command(name="start")
def start_server(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(getattr(settings, "api_port", 8000), help="Port to bind to"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
    log_level: str = typer.Option("info", help="Log level (debug, info, warning, error)"),
    log_dir: Optional[str] = typer.Option(None, help="Directory for log files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress console output except errors"
    ),
) -> None:
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


***REMOVED*** Alias for convenience (so users can run either "serve" or "serve start")
@app.callback(invoke_without_command=True)
def serve(ctx: typer.Context) -> None:
    """Start the backend API server."""
    if ctx.invoked_subcommand is None:
        start_server()
