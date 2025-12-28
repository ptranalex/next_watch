"""Command for launching an interactive interface for data import operations."""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from data_importer.cli.utils import get_api_key, print_config
from data_importer.config.app import (
    DEFAULT_LOGS_DIR,
    DEFAULT_OMDB_API_KEY,
    DEFAULT_QUIET,
    DEFAULT_TMDB_ACCESS_TOKEN,
    DEFAULT_VERBOSE,
    Config,
)
from data_importer.config.logging import configure_logging

logger = logging.getLogger("data_importer.cli.commands.interactive")
console = Console()


def interactive(
    logs_dir: Path = typer.Option(
        DEFAULT_LOGS_DIR,
        "--logs-dir",
        "-l",
        help="Directory to save log files.",
    ),
    tmdb_access_token: Optional[str] = typer.Option(
        DEFAULT_TMDB_ACCESS_TOKEN,
        "--tmdb-token",
        "-t",
        help="TMDB Bearer token (or set TMDB_ACCESS_TOKEN environment variable)",
    ),
    omdb_api_key: Optional[str] = typer.Option(
        DEFAULT_OMDB_API_KEY,
        "--omdb-key",
        "-o",
        help="OMDB API key (or set OMDB_API_KEY environment variable)",
    ),
    verbose: bool = typer.Option(
        DEFAULT_VERBOSE,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    quiet: bool = typer.Option(
        DEFAULT_QUIET,
        "--quiet",
        "-q",
        help="Suppress non-essential output",
    ),
) -> None:
    """Launch an interactive interface for data import operations.

    This command provides a conversational way to interact with movie data sources
    and import operations without having to write code.

    API Keys:
        - TMDB: Get from https://www.themoviedb.org/settings/api
        - OMDB: Get from https://www.omdbapi.com/apikey.aspx

    Note:
        This feature is experimental and not fully implemented yet.

    Example:
        data-importer interactive --verbose
    """
    ***REMOVED*** Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(
        log_level=log_level,
        log_dir=logs_dir,
        verbose=verbose,
        quiet=quiet,
    )

    logger.debug("Interactive mode started")

    try:
        ***REMOVED*** Create directories if they don't exist
        logs_dir.mkdir(parents=True, exist_ok=True)

        ***REMOVED*** Get API keys
        tmdb_access_token = get_api_key(
            tmdb_access_token,
            "TMDB_ACCESS_TOKEN",
            "TMDB access token",
            console,
            required=False,
        )
        omdb_api_key = get_api_key(
            omdb_api_key, "OMDB_API_KEY", "OMDB API key", console, required=False
        )

        ***REMOVED*** Create config object
        config = Config(
            logs_dir=logs_dir,
            log_level=log_level,
            verbose=verbose,
            quiet=quiet,
            tmdb_access_token=tmdb_access_token,
            omdb_api_key=omdb_api_key,
        )

        ***REMOVED*** Display the config
        print_config(config, title="Interactive Mode Configuration", console=console)

        ***REMOVED*** Validate that credentials were provided (interactive mode is not implemented yet)
        if tmdb_access_token:
            console.print("[green]TMDB access token set[/green]")
        else:
            console.print("[yellow]TMDB access token not set[/yellow]")

        if omdb_api_key:
            console.print("[green]OMDB API key set[/green]")
        else:
            console.print("[yellow]OMDB API key not set[/yellow]")

        ***REMOVED*** Display experimental notice
        console.print("\n[bold yellow]EXPERIMENTAL FEATURE[/bold yellow]")
        console.print("[yellow]Interactive mode is not fully implemented yet.[/yellow]")
        console.print("[green]Interactive mode initialized[/green]")
        console.print("Type 'exit' or 'quit' to end the session")

        ***REMOVED*** Placeholder for interactive loop
        console.print("[yellow]Interactive mode not yet implemented[/yellow]")

    except Exception as e:
        logger.error(f"Error in interactive session: {str(e)}")
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
