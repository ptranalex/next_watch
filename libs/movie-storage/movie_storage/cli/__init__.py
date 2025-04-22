"""Command-line interface package."""

import typer

***REMOVED*** Create main app
app = typer.Typer(
    help="Movie Storage Database Management",
    add_completion=False,
)

***REMOVED*** Make app available for importing
__all__ = ["app"]

***REMOVED*** Import commands at the end to avoid circular imports
from movie_storage.cli import commands
