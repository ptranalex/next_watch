"""Command for launching an interactive shell with data_importer modules."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict

import typer
from rich import pretty, print_json
from rich.console import Console
from rich.pretty import pprint

from data_importer.cli.commands.shell.help import create_shell_help_function, get_banner_text
from data_importer.cli.commands.shell.helpers import async_run, create_loading_functions
from data_importer.cli.commands.shell.repl import configure_repl
from data_importer.cli.utils import get_api_key, print_config, print_plain
from data_importer.config.app import (
    DEFAULT_DATA_DIR,
    DEFAULT_IMDB_API_KEY,
    DEFAULT_LOGS_DIR,
    DEFAULT_OMDB_API_KEY,
    DEFAULT_QUIET,
    DEFAULT_TMDB_ACCESS_TOKEN,
    DEFAULT_VERBOSE,
    Config,
)
from data_importer.config.logging import configure_logging
from data_importer.services import IMDBClient, OMDBClient, TMDBClient

logger = logging.getLogger("data_importer.cli.shell.command")
console = Console()


def shell(
    logs_dir: Path = typer.Option(
        DEFAULT_LOGS_DIR,
        "--logs-dir",
        "-l",
        help="Directory to save log files.",
    ),
    data_dir: Path = typer.Option(
        DEFAULT_DATA_DIR,
        "--data-dir",
        "-d",
        help="Directory for movie data files.",
    ),
    tmdb_access_token: str = typer.Option(
        DEFAULT_TMDB_ACCESS_TOKEN,
        "--tmdb-token",
        "-t",
        help="TMDB Bearer token (or set TMDB_ACCESS_TOKEN environment variable)",
    ),
    imdb_api_key: str = typer.Option(
        DEFAULT_IMDB_API_KEY,
        "--imdb-api-key",
        "-i",
        help="IMDb API key (or set IMDB_API_KEY environment variable)",
    ),
    omdb_api_key: str = typer.Option(
        DEFAULT_OMDB_API_KEY,
        "--omdb-api-key",
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
    theme: str = typer.Option(
        "monokai",
        "--theme",
        "-th",
        help="Color theme for the shell (default, monokai, solarized, pastie, vs, manni, autumn, murphy, monochrome)",
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        "-p",
        help="Use plain output without syntax highlighting",
    ),
) -> None:
    """Launch an interactive shell with pre-loaded data_importer modules.

    This shell provides a powerful interactive environment with:
    - Auto-imported data services (TMDB, IMDb)
    - Pre-configured clients for movie data
    - Helper functions for common operations
    - Code completion and syntax highlighting

    Examples:
        - Get popular movies: movies = run_async(tmdb_client.get_popular_movies())
        - Get movies by year: movies = run_async(tmdb_client.fetch_movies_by_year(2023))
        - Get top IMDb movies: movies = imdb_client.get_top_movies(limit=10)
    """
    ***REMOVED*** Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(
        log_level=log_level,
        log_dir=logs_dir,
        verbose=verbose,
        quiet=quiet,
    )

    logger.debug("Shell command started")

    try:
        ***REMOVED*** Create directories if they don't exist
        logs_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        ***REMOVED*** Ensure API keys are available
        tmdb_access_token = get_api_key(
            tmdb_access_token, "TMDB_ACCESS_TOKEN", "TMDB access token", console, required=False
        )
        imdb_api_key = get_api_key(
            imdb_api_key, "IMDB_API_KEY", "IMDb API key", console, required=False
        )
        omdb_api_key = get_api_key(
            omdb_api_key, "OMDB_API_KEY", "OMDB API key", console, required=False
        )

        ***REMOVED*** Create config
        config = Config(
            logs_dir=logs_dir,
            data_dir=data_dir,
            tmdb_access_token=tmdb_access_token,
            imdb_api_key=imdb_api_key,
            omdb_api_key=omdb_api_key,
            log_level=log_level,
            verbose=verbose,
            quiet=quiet,
        )

        ***REMOVED*** Display the config
        print_config(config, title="Shell Configuration", console=console)

        ***REMOVED*** Check if ptpython is installed
        try:
            from ptpython.repl import embed
        except ImportError:
            console.print("[red]Error: ptpython is not installed.[/red]")
            console.print(
                "Install it with: [bold]pip install ptpython[/bold] or [bold]poetry add ptpython[/bold]"
            )
            raise typer.Exit(1)

        ***REMOVED*** Create client instances
        tmdb_client = TMDBClient(
            access_token=tmdb_access_token,
            base_url="https://api.themoviedb.org/3",
        )
        imdb_client = IMDBClient()
        omdb_client = OMDBClient(
            api_key=omdb_api_key,
            base_url="http://www.omdbapi.com",
        )

        ***REMOVED*** TMDB API key warning
        if not tmdb_access_token:
            console.print(
                "[yellow]! TMDB access token not set. API calls will fail without authentication.[/yellow]"
            )
            console.print("  Get a bearer token from your TMDB account settings")

        ***REMOVED*** OMDB API key warning
        if not omdb_api_key:
            console.print(
                "[yellow]! OMDB API key not set. API calls will fail without authentication.[/yellow]"
            )
            console.print("  Get an API key from: https://www.omdbapi.com/apikey.aspx")

        ***REMOVED*** Create the shell help function
        shell_help: Callable[[], None] = create_shell_help_function(namespace={})

        ***REMOVED*** Install pretty printer for the shell session
        pretty.install()

        ***REMOVED*** Get the banner text
        banner = get_banner_text()

        ***REMOVED*** Display the banner with help information
        console.print(banner)

        ***REMOVED*** Create the namespace with all available functionality
        namespace: Dict[str, Any] = {
            "tmdb_client": tmdb_client,
            "imdb_client": imdb_client,
            "omdb_client": omdb_client,
            "config": config,
            "print_plain": print_plain,
            "print_json": print_json,
            "print_config": print_config,
            "pprint": pprint,
            "pp": pprint,
            "help": shell_help,
            "async_run": async_run,
            "console": console,
        }

        ***REMOVED*** Add utility functions to namespace
        create_loading_functions(namespace)

        ***REMOVED*** Get the banner text
        theme_text = "plain (no highlighting)" if plain else theme

        ***REMOVED*** Launch ptpython with configuration
        embed(
            globals=namespace,
            history_filename=os.path.expanduser("~/.data_importer_history"),
            title="Next Watch Data Importer Shell",
            configure=lambda repl: configure_repl(repl, theme=theme, plain=plain),
        )

        ***REMOVED*** Cleanup async resources
        try:
            asyncio.run(tmdb_client.close())
            asyncio.run(omdb_client.close())
        except:
            pass

    except Exception as e:
        logger.exception(f"Error in shell session: {str(e)}")
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
