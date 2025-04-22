"""Database migration commands."""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from movie_storage.config.app import Config
from movie_storage.config.logging import configure_logging
from movie_storage.db.migrations import run_migration

***REMOVED*** Create app for this command group
app = typer.Typer(help="Database migration commands")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    log_level: str = typer.Option("INFO", help="Logging level", show_default=True),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress non-essential output"
    ),
    database_url: Optional[str] = typer.Option(
        None, help="Database URL (overrides config)"
    ),
):
    """Run database migrations to update schema."""
    ***REMOVED*** Configure logging
    configure_logging(log_level=log_level, verbose=verbose, quiet=quiet)

    ***REMOVED*** Get configuration
    config = Config.get_instance()
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Show config if verbose
    if verbose and not quiet:
        masked_url = config._mask_database_password(config.database_url)
        console.print(f"[bold blue]Database URL:[/] {masked_url}")

    ***REMOVED*** Run migrations
    with console.status("[bold green]Running database migrations...[/]"):
        applied_migrations = run_migration(db_url=database_url, config=config)

    ***REMOVED*** Show results
    if not quiet:
        if applied_migrations:
            table = Table(title="Applied Migrations")
            table.add_column("ID", style="cyan")

            for migration_id in applied_migrations:
                table.add_row(migration_id)

            console.print(table)
            console.print(
                f"[bold green]✓[/] Applied {len(applied_migrations)} migrations successfully!"
            )
        else:
            console.print("[bold blue]ℹ[/] Database schema is already up to date!")

    return 0


***REMOVED*** Register with parent app
from movie_storage.cli import app as cli_app

cli_app.add_typer(app, name="migrate")
