"""Data importer CLI module."""

import logging
import sys
import typer
from rich.console import Console
from rich.traceback import install

from data_importer.cli.commands.shell import shell
from data_importer.cli.commands.interactive import interactive
from data_importer.config import DEFAULT_LOGS_DIR, configure_logging, with_logging

***REMOVED*** CLI commands
from data_importer.cli.commands import import_movie
from data_importer.cli.commands import sync

***REMOVED*** Install rich traceback handler
install()

***REMOVED*** Initialize Typer app
app = typer.Typer(
    name="data-importer",
    help="Import movie and TV show data from various sources.",
    add_completion=False,
)

***REMOVED*** Configure basic logging
configure_logging(log_level="INFO", log_dir=DEFAULT_LOGS_DIR, verbose=False, quiet=False)

logger = logging.getLogger("data_importer.cli")

***REMOVED*** Add command groups
app.add_typer(import_movie.app, name="movie")
app.add_typer(sync.app, name="sync")

***REMOVED*** Add commands to the app
app.command(name="shell", help="Launch an interactive shell")(shell)
app.command(name="interactive", help="Launch an interactive shell")(interactive)


@with_logging(log_level="INFO", log_dir=DEFAULT_LOGS_DIR)
def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        sys.exit(1)


__all__ = ["app", "main"]
