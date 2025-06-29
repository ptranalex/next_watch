"""Main CLI entry point for ML API.

This module provides the primary CLI interface for the ML API,
following the standardized CLI patterns from the cli library.
"""

import sys
from typing import Any

import typer
from rich.console import Console

from ml_api import __version__

***REMOVED*** Configure CLI app
app = typer.Typer(
    name="ml-api",
    help="Machine Learning API for Next Watch platform",
    rich_markup_mode="rich",
    add_completion=False,
)

console = Console()


@app.command("version")
def version() -> None:
    """Show version information."""
    console.print(f"ML API version: [bold cyan]{__version__}[/]")


def main() -> Any:
    """Main CLI entry point."""
    try:
        return app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
