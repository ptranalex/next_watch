"""Server command for BFF API."""

import logging
import typer
from typer import Typer
import uvicorn
from typing import Dict, Any, Optional
from rich.console import Console

from bff_api.config.app import settings, Config
from bff_api.cli.utils import print_config
from bff_api.main import create_app

app: Typer = typer.Typer(name="serve", help="Server commands for running the BFF API.")
console = Console()
logger = logging.getLogger(__name__)


@app.callback(invoke_without_command=True)
def serve_callback(ctx: typer.Context) -> None:
    """Server commands for running the BFF API."""
    ***REMOVED*** When no subcommand is provided, run the start command with default args
    if ctx.invoked_subcommand is None:
        ***REMOVED*** Pass empty values to avoid OptionInfo objects being used
        ctx.invoke(
            start, host=None, port=None, reload=False, log_level=None, verbose=False, quiet=False
        )


@app.command(name="start")
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
        if log_level and isinstance(log_level, str):
            config_kwargs["log_level"] = log_level.upper()

        ***REMOVED*** Update global settings if any CLI overrides are provided
        if config_kwargs:
            config = Config(**config_kwargs)
        else:
            config = settings

        ***REMOVED*** Get the actual host and port values from config (not OptionInfo objects)
        host_value = config.host
        port_value = config.port

        ***REMOVED*** Display configuration unless quiet mode
        if not quiet:
            if verbose:
                print_config(config, "BFF Server Configuration", console)
            else:
                console.print(f"[blue]Starting BFF API server on {host_value}:{port_value}[/blue]")
                console.print(
                    f"[dim]Environment: {config.environment} | Debug: {config.debug}[/dim]"
                )

        ***REMOVED*** Configure logging level
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        elif quiet:
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=getattr(logging, config.log_level))

        logger.info(f"Starting BFF API server on {host_value}:{port_value}")

        if verbose:
            logger.debug(f"Configuration: host={host_value}, port={port_value}, reload={reload}")

        ***REMOVED*** Start server
        if reload:
            ***REMOVED*** Use import string for reload mode
            uvicorn.run(
                "bff_api.main:app",
                host=host_value,
                port=port_value,
                reload=reload,
                log_level=config.log_level.lower(),
                access_log=not config.is_production,
            )
        else:
            ***REMOVED*** Use app instance for production mode (more efficient)
            fastapi_app = create_app()
            uvicorn.run(
                fastapi_app,
                host=host_value,
                port=port_value,
                reload=reload,
                log_level=config.log_level.lower(),
                access_log=not config.is_production,
            )

    except Exception as e:
        console.print(f"[bold red]Error starting server: {e}[/bold red]")
        logger.error(f"Failed to start server: {e}")
        raise typer.Exit(code=1)
