"""Database initialization commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from movie_storage.config.app import Config
from movie_storage.config.logging import with_logging
from movie_storage.db.db import init_db

***REMOVED*** Create app for this command group
app = typer.Typer(help="Database initialization commands")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    create_tables: bool = typer.Option(False, "--create-tables", help="Create database tables"),
    database_url: Optional[str] = typer.Option(None, help="Database URL (overrides config)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
) -> int:
    """Initialize the database and optionally create tables."""
    ***REMOVED*** Get configuration
    config = Config.get_instance()
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Show config if verbose
    if verbose and not quiet:
        masked_url = config._mask_database_password(config.database_url)
        console.print(f"[bold blue]Database URL:[/] {masked_url}")

    ***REMOVED*** Initialize database
    with console.status("[bold green]Initializing database...[/]"):
        init_db(
            db_url=database_url,
            create_tables=create_tables,
            config=config,
        )

    ***REMOVED*** Show results
    if not quiet:
        if create_tables:
            console.print("[bold green]✓[/] Database initialized and tables created successfully!")
        else:
            console.print("[bold green]✓[/] Database initialized successfully!")
            console.print("[dim]Use --create-tables to create database tables.[/dim]")

    return 0


***REMOVED*** Register with parent app
from movie_storage.cli import app as cli_app

cli_app.add_typer(app, name="init")
