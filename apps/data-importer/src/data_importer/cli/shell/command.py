"""Command for launching an interactive shell with data_importer modules."""

import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict

import typer
from rich import pretty
from rich.console import Console
from rich.pretty import pprint

from .help import create_shell_help_function, get_banner_text
from .helpers import async_run, create_loading_functions, print_plain
from .repl import configure_repl

logger = logging.getLogger("data_importer.cli.shell.command")
console = Console()

***REMOVED*** Default configuration
DEFAULT_CONFIG_DIR = Path.home() / ".data_importer" / "config"
DEFAULT_LOGS_DIR = Path.home() / ".data_importer" / "logs"
DEFAULT_CACHE_DIR = Path.home() / ".data_importer" / "cache"
DEFAULT_VERBOSE = False
DEFAULT_QUIET = False


def shell(
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
    cache_dir: Path = typer.Option(
        DEFAULT_CACHE_DIR,
        "--cache-dir",
        "-d",
        help="Directory for cache files.",
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
    - Auto-imported data services
    - Helper functions for common operations
    - Code completion and syntax highlighting

    Examples:
        - Import movies from TMDb: tmdb_client.import_movies(path)
        - Import movies from IMDb: imdb_client.get_top_movies(limit=10)
    """
    ***REMOVED*** Configure logging
    log_level = "DEBUG" if verbose else "INFO"

    logger.debug("Shell command started")

    try:
        ***REMOVED*** Create directories if they don't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)

        ***REMOVED*** Display relevant configuration
        config_args = {
            "config_dir": config_dir,
            "logs_dir": logs_dir,
            "cache_dir": cache_dir,
            "verbose": verbose,
            "quiet": quiet,
            "theme": theme,
        }

        ***REMOVED*** Pretty print configuration
        console.print("\n[bold]Data Importer Shell Configuration:[/bold]")
        for key, value in config_args.items():
            console.print(f"  [cyan]{key}:[/cyan] {value}")
        console.print()

        ***REMOVED*** Check if ptpython is installed
        try:
            from ptpython.repl import embed
        except ImportError:
            console.print("[red]Error: ptpython is not installed.[/red]")
            console.print(
                "Install it with: [bold]pip install ptpython[/bold] or [bold]poetry add ptpython[/bold]"
            )
            raise typer.Exit(1)

        ***REMOVED*** Import core modules
        import asyncio

        ***REMOVED*** Import the data services
        from data_importer.services import TMDBClient, IMDBClient

        ***REMOVED*** Create instances of clients
        tmdb_client = TMDBClient()
        imdb_client = IMDBClient()

        ***REMOVED*** Set up a namespace for the shell
        namespace = {
            "asyncio": asyncio,
            "console": console,
            "pprint": pprint,
            "print_plain": print_plain,
            "tmdb_client": tmdb_client,
            "imdb_client": imdb_client,
        }

        ***REMOVED*** Add async run helper
        namespace["run"] = async_run

        ***REMOVED*** Create help function
        namespace["help"] = create_shell_help_function(namespace)

        ***REMOVED*** Add loading functions
        create_loading_functions(namespace)

        ***REMOVED*** Set up pretty printing
        pretty.install()

        ***REMOVED*** Configure and launch the REPL
        configure_repl(embed, namespace, theme, quiet, plain)

        console.print("\n[green]Data Importer shell session ended.[/green]")

    except Exception as e:
        logger.exception(f"Error in shell command: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
