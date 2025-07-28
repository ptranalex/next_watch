"""Server commands for the Recommendation API CLI."""

from typing import Union, Dict, Any
import typer
from typer import Typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from recommendation_api.config.app import settings, Config
from recommendation_api.cli.utils import print_error, print_success
from config.logging import configure_logging, get_logger

app: Typer = typer.Typer(
    name="serve",
    help="Start the Recommendation API server",
)

console = Console()
logger = get_logger("recommendation_api.cli.commands.serve")


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging for serve commands.

    Args:
        verbose: Enable verbose logging
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging based on verbosity
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"

    configure_logging(
        log_level=log_level,
        verbose=verbose,
        quiet=quiet,
        logger_name="recommendation_api",
        color_theme="modern",
        http_verbose=False,
    )


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
    workers: int = typer.Option(
        None,
        "--workers",
        "-w",
        help="Number of worker processes",
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
        workers: Number of worker processes
        log_level: Logging level for the application
        verbose: Enable verbose console output
        quiet: Suppress console output except errors
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

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
        if workers:
            config.workers = workers

        ***REMOVED*** Display server configuration
        console.print(
            Panel.fit(
                f"Starting Recommendation API server on {config.host}:{config.port}",
                title="Server Start",
                border_style="green",
            )
        )

        if verbose:
            ***REMOVED*** Create server config table
            table = Table(title="Server Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Host", config.host)
            table.add_row("Port", str(config.port))
            table.add_row("Workers", str(config.workers))
            table.add_row("Log Level", config.log_level)
            table.add_row("Auto-reload", "Enabled" if config.reload else "Disabled")

            console.print(table)

        logger.info(f"Starting server on {config.host}:{config.port}")

        ***REMOVED*** Start server with specific parameters
        ***REMOVED*** Define workers only if specified and not in reload mode
        workers_param = config.workers if config.workers and not config.reload else None

        uvicorn.run(
            "recommendation_api.main:app",
            host=config.host,
            port=config.port,
            reload=config.reload,
            log_level=config.log_level.lower(),
            workers=workers_param,
        )

    except Exception as e:
        print_error(f"Failed to start server: {str(e)}", console)
        if verbose:
            logger.exception("Server start error")
        raise typer.Exit(code=1)


@app.command()
def stop(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed stop information",
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Stop the Recommendation API server.

    Args:
        verbose: Show detailed stop information
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    try:
        console.print("[yellow]Stopping Recommendation API server...[/yellow]")
        ***REMOVED*** TODO: Implement graceful shutdown logic
        console.print("[yellow]Note: This feature is not yet implemented[/yellow]")
        console.print(
            "[yellow]To stop the server, press Ctrl+C in the terminal where it's running[/yellow]"
        )

        print_success("Server stopped successfully", console)
    except Exception as e:
        print_error("Failed to stop server", console, e)
        if verbose:
            logger.exception("Server stop error")
        raise typer.Exit(code=1)


@app.command()
def restart(
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
    workers: int = typer.Option(
        None,
        "--workers",
        "-w",
        help="Number of worker processes",
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
    """Restart the Recommendation API server.

    Args:
        host: Host address to bind the server to
        port: Port number to bind the server to
        reload: Whether to enable auto-reload for development
        workers: Number of worker processes
        log_level: Logging level for the application
        verbose: Enable verbose console output
        quiet: Suppress console output except errors
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    try:
        console.print("[yellow]Restarting Recommendation API server...[/yellow]")
        stop(verbose=verbose, quiet=quiet)
        start(
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
            verbose=verbose,
            quiet=quiet,
        )
    except Exception as e:
        print_error(f"Failed to restart server: {str(e)}", console)
        if verbose:
            logger.exception("Server restart error")
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def serve_main(ctx: typer.Context) -> None:
    """Server management commands.

    This command group provides tools for managing the Recommendation API server,
    including starting, stopping, and restarting the server.
    """
    if ctx.invoked_subcommand is None:
        start()
