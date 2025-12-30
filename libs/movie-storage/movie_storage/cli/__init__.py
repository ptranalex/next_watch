"""Command-line interface package."""

import typer

# Create main app
app = typer.Typer(
    help="Movie Storage Database Management",
    add_completion=False,
)

# Make app available for importing
__all__ = ["app"]

# Import commands at the end to avoid circular imports
from movie_storage.cli import commands
