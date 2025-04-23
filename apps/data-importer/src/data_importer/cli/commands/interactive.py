"""Command for launching an interactive interface for data import operations."""

import logging
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from data_importer.config.app import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_LOGS_DIR,
    DEFAULT_QUIET,
    DEFAULT_VERBOSE,
    DEFAULT_TMDB_ACCESS_TOKEN,
    DEFAULT_OMDB_API_KEY,
    Config,
)
from data_importer.config.logging import configure_logging
from data_importer.cli.utils import print_config, get_api_key
from data_importer.services.tmdb import TMDBClient
from data_importer.services.omdb import OMDBClient

logger = logging.getLogger("data_importer.cli.commands.interactive")
console = Console()


def interactive(
    config_dir: Path = typer.Option(
        DEFAULT_CONFIG_DIR,
        "--config-dir",
        "-c",
        help="Configuration directory for app settings.",
    ),
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
        config_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        ***REMOVED*** Get API keys
        tmdb_access_token = get_api_key(
            tmdb_access_token, "TMDB_ACCESS_TOKEN", "TMDB access token", console, required=False
        )
        omdb_api_key = get_api_key(
            omdb_api_key, "OMDB_API_KEY", "OMDB API key", console, required=False
        )

        ***REMOVED*** Create config object
        config = Config(
            config_dir=config_dir,
            logs_dir=logs_dir,
            log_level=log_level,
            verbose=verbose,
            quiet=quiet,
            tmdb_access_token=tmdb_access_token,
            omdb_api_key=omdb_api_key,
        )

        ***REMOVED*** Display the config
        print_config(config, title="Interactive Mode Configuration", console=console)

        ***REMOVED*** Initialize movie data clients if keys are provided
        if tmdb_access_token:
            tmdb_client = TMDBClient(access_token=tmdb_access_token)
            console.print("[green]TMDB client initialized successfully[/green]")
        else:
            console.print("[yellow]TMDB client not initialized (no API key)[/yellow]")

        if omdb_api_key:
            omdb_client = OMDBClient(api_key=omdb_api_key)
            console.print("[green]OMDB client initialized successfully[/green]")
        else:
            console.print("[yellow]OMDB client not initialized (no API key)[/yellow]")

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
