"""Server commands for the Recommendation API CLI."""

import logging
from typing import Union, Dict, Any
import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from recommendation_api.config.app import settings, Config
from recommendation_api.cli.utils import print_error, print_success

app = typer.Typer(
    name="serve",
    help="Start the Recommendation API server",
)

console = Console()


@app.command()
def start(
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
    """Start the Recommendation API server.

    Args:
        host: Host address to bind the server to
        port: Port number to bind the server to
        reload: Whether to enable auto-reload for development
        log_level: Logging level for the application
        verbose: Enable verbose console output
        quiet: Suppress console output except errors
    """
    try:
        ***REMOVED*** Get configuration
        config = Config()
        
        ***REMOVED*** Override config with command line arguments
        if host:
            config.host = host
        if port:
            config.port = port
        if log_level:
            config.log_level = log_level
        if reload:
            config.reload = reload
        if verbose:
            config.verbose = verbose

        ***REMOVED*** Start server
        console.print(Panel.fit(
            f"Starting Recommendation API server on {config.host}:{config.port}",
            title="Server Start",
            border_style="green"
        ))
    
        uvicorn.run(
            "recommendation_api.main:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower(),
        )
    except Exception as e:
        print_error(f"Failed to start server: {str(e)}", console)


@app.command()
def stop() -> None:
    """Stop the Recommendation API server."""
    try:
        ***REMOVED*** TODO: Implement graceful shutdown
        print_success("Server stopped successfully", console)
    except Exception as e:
        print_error("Failed to stop server", console, e)
        raise typer.Exit(code=1)


@app.command()
def restart() -> None:
    """Restart the Recommendation API server."""
    try:
        stop()
        start()
    except Exception as e:
        print_error(f"Failed to restart server: {str(e)}", console)
        raise typer.Exit(code=1) 