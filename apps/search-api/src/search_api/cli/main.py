"""Main CLI entry point for Search API."""

import typer
from rich.console import Console

from search_api.cli.commands import redis

console = Console()

# Create main app
app = typer.Typer(
    name="search-api",
    help="Search API CLI for managing search suggestions and Redis data.",
    add_completion=False,
)

# Add command groups
app.add_typer(redis.app, name="redis", help="Redis data management commands")


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold blue]Search API[/bold blue] version [green]0.1.0[/green]")


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
