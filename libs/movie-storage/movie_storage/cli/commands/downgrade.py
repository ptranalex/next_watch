"""Database downgrade commands."""

import importlib
from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from sqlalchemy import text, Engine

from movie_storage.config.app import Config
from movie_storage.config.logging import with_logging
from movie_storage.db.db import get_engine
from movie_storage.db.migrations import get_applied_migrations

***REMOVED*** Create app for this command group
app = typer.Typer(help="Database downgrade commands")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    all: bool = typer.Option(False, "--all", help="Downgrade all migrations"),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm destructive operation"),
    database_url: Optional[str] = typer.Option(None, help="Database URL (overrides config)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
) -> int:
    """Downgrade the database by reverting migrations."""
    if not confirm:
        console.print("[bold red]Error:[/] Downgrade requires --confirm flag due to data loss risk")
        if not quiet:
            console.print("Run with --confirm to proceed with the downgrade.")
        raise typer.Exit(code=1)

    ***REMOVED*** Get configuration
    config = Config.get_instance()
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Show config if verbose
    if verbose and not quiet:
        masked_url = config._mask_database_password(config.database_url)
        console.print(f"[bold blue]Database URL:[/] {masked_url}")

    ***REMOVED*** Get engine and migrations
    engine = get_engine(database_url, config)
    migrations = get_applied_migrations(engine)

    if not migrations:
        console.print("[bold blue]ℹ[/] No migrations to downgrade.")
        raise typer.Exit(code=0)

    ***REMOVED*** Sort migration IDs
    migration_ids = sorted(migrations.keys())

    ***REMOVED*** Process migrations to downgrade
    if all:
        ***REMOVED*** Final confirmation for downgrading all migrations
        if not confirm or (
            not quiet
            and not Confirm.ask(
                "[bold red]Warning:[/] You are about to downgrade ALL migrations. This will reset your database schema completely. Continue?"
            )
        ):
            console.print("[bold yellow]Downgrade cancelled.[/]")
            raise typer.Exit(code=1)

        if not quiet:
            console.print("[bold yellow]Downgrading all migrations...[/]")

        ***REMOVED*** Process migrations in reverse order
        for migration_id in reversed(migration_ids):
            success = _downgrade_single_migration(
                engine, migration_id, migrations[migration_id], verbose, quiet
            )
            if not success:
                raise typer.Exit(code=1)

        if not quiet:
            console.print("[bold green]✓[/] All migrations successfully downgraded!")
    else:
        ***REMOVED*** Just downgrade the last migration
        last_migration_id = migration_ids[-1]
        last_migration_desc = migrations[last_migration_id]

        if not quiet:
            console.print(
                f"[bold]Downgrading migration:[/] {last_migration_id} - {last_migration_desc}"
            )

        success = _downgrade_single_migration(
            engine, last_migration_id, last_migration_desc, verbose, quiet
        )
        if not success:
            raise typer.Exit(code=1)

        if not quiet:
            console.print(
                f"[bold green]✓[/] Successfully downgraded migration: {last_migration_id}"
            )

    return 0


def _downgrade_single_migration(
    engine: Engine, migration_id: str, migration_desc: str, verbose: bool, quiet: bool
) -> bool:
    """Downgrade a single migration.

    Args:
        engine: SQLAlchemy engine
        migration_id: Migration ID
        migration_desc: Migration description
        verbose: Whether to show verbose output
        quiet: Whether to suppress non-essential output

    Returns:
        Success status
    """
    ***REMOVED*** Show progress if not quiet
    if not quiet:
        console.print(f"[bold yellow]⟳[/] Downgrading: {migration_id}")

    ***REMOVED*** Import the migration module
    try:
        module = importlib.import_module(f"movie_storage.db.migrations.{migration_id}")
    except ImportError as e:
        console.print(f"[bold red]Error:[/] Could not import migration module: {migration_id}")
        if verbose:
            console.print(f"[red]{str(e)}[/]")
        return False

    ***REMOVED*** Call the downgrade function
    try:
        with console.status("Running downgrade..."):
            module.downgrade(engine)
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to downgrade migration {migration_id}")
        if verbose:
            console.print(f"[red]{str(e)}[/]")
        return False

    ***REMOVED*** Remove the migration record
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM migrations WHERE id = :id"),
                {"id": migration_id},
            )
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to remove migration record for {migration_id}")
        if verbose:
            console.print(f"[red]{str(e)}[/]")
        return False

    return True


***REMOVED*** Register with parent app
from movie_storage.cli import app as cli_app

cli_app.add_typer(app, name="downgrade")
