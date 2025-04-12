"""CLI package for the data_importer module."""

import logging
import sys
import typer

from data_importer.cli.shell import shell

***REMOVED*** Initialize Typer app
app = typer.Typer(
    name="data-importer",
    help="Next Watch Data Importer CLI",
    add_completion=True,
    no_args_is_help=True,
)

logger = logging.getLogger("data_importer.cli")

***REMOVED*** Add commands to the app
app.command(name="shell", help="Launch an interactive shell")(shell)

***REMOVED*** Define CLI object for main.py to import
cli = app


def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        sys.exit(1)


__all__ = ["app", "main", "cli"]
