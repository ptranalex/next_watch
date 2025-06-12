"""Server command for BFF API."""

import typer
from typer import Typer
import uvicorn
from typing import Dict, Any, Optional

from bff_api.cli.logging import get_cli_output

app: Typer = typer.Typer(name="serve", help="Server commands for running the BFF API.")


@app.callback(invoke_without_command=True)
def serve_callback(
    ctx: typer.Context,
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
    """Server commands for running the BFF API."""
    ***REMOVED*** When no subcommand is provided, run the start command with args from command line
    if ctx.invoked_subcommand is None:
        ***REMOVED*** Forward the parameters from the command line to the start command
        ctx.invoke(
            start,
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            verbose=verbose,
            quiet=quiet,
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
    out = get_cli_output("serve", verbose=verbose, quiet=quiet)

    try:
        ***REMOVED*** Import only when needed (no auto-logging)
        from bff_api.config.app import get_settings, Config
        from bff_api.cli.utils import print_config
        from bff_api.main import get_app  ***REMOVED*** Use lazy loading

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
            config = get_settings()  ***REMOVED*** Get actual Config instance

        ***REMOVED*** Get the actual host and port values from config
        host_value = config.host
        port_value = config.port

        ***REMOVED*** Display configuration unless quiet mode
        if not quiet:
            if verbose:
                print_config(config, "BFF Server Configuration", out.console)
            else:
                out.info(f"[blue]Starting BFF API server on {host_value}:{port_value}[/blue]")
                out.info(f"[dim]Environment: {config.environment} | Debug: {config.debug}[/dim]")

        ***REMOVED*** Log operational info
        out.log_operation(
            "Starting BFF API server",
            host=host_value,
            port=port_value,
            reload=reload,
            environment=config.environment,
        )

        ***REMOVED*** Start server - the get_app() call will configure full logging for web server
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
            ***REMOVED*** Use app instance for production mode - this triggers full logging setup
            fastapi_app = get_app()
            uvicorn.run(
                fastapi_app,
                host=host_value,
                port=port_value,
                reload=reload,
                log_level=config.log_level.lower(),
                access_log=not config.is_production,
            )

    except Exception as e:
        out.error(f"Error starting server: {e}")
        out.log_error("Server start failed", e)
        raise typer.Exit(code=1)
