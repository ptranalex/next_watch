"""CLI package for the data_importer module."""

import logging
import sys
import typer

from data_importer.cli.commands.shell import shell
from data_importer.cli.commands.interactive import interactive
from data_importer.config import DEFAULT_LOGS_DIR, configure_logging, with_logging

***REMOVED*** Initialize Typer app
app = typer.Typer(
    name="data-importer",
    help="Next Watch Data Importer CLI",
    add_completion=True,
    no_args_is_help=True,
)

***REMOVED*** Configure basic logging
configure_logging(log_level="INFO", log_dir=DEFAULT_LOGS_DIR, verbose=False, quiet=False)

logger = logging.getLogger("data_importer.cli")

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
