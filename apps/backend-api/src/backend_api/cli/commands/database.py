"""Database management commands for the Backend API CLI."""

import importlib
from pathlib import Path
from typing import Optional, List, Dict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import text, Engine

from backend_api.config.app import Config
from backend_api.config.logging import configure_logging, get_logger
from backend_api.db.db import init_db, get_engine
from backend_api.db.migrations import run_migration, get_applied_migrations

***REMOVED*** Create app for database commands
app = typer.Typer(help="Database management commands")
console = Console()


***REMOVED*** ============================================================================
***REMOVED*** Database Initialization
***REMOVED*** ============================================================================


@app.command("init")
def init_database(
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


***REMOVED*** ============================================================================
***REMOVED*** Database Migrations
***REMOVED*** ============================================================================


@app.command("migrate")
def migrate_database(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    log_level: str = typer.Option("INFO", help="Logging level", show_default=True),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
    database_url: Optional[str] = typer.Option(None, help="Database URL (overrides config)"),
) -> int:
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


***REMOVED*** ============================================================================
***REMOVED*** Database Downgrades
***REMOVED*** ============================================================================


@app.command("downgrade")
def downgrade_database(
    steps: int = typer.Option(1, "--steps", "-s", help="Number of migrations to downgrade"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Target migration ID"),
    all_migrations: bool = typer.Option(False, "--all", help="Downgrade all migrations"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    log_level: str = typer.Option("INFO", help="Logging level", show_default=True),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
    database_url: Optional[str] = typer.Option(None, help="Database URL (overrides config)"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Confirm before downgrading"),
) -> int:
    """Downgrade database migrations."""
    ***REMOVED*** Configure logging
    configure_logging(log_level=log_level, verbose=verbose, quiet=quiet)
    logger = get_logger(__name__)

    ***REMOVED*** Get configuration
    config = Config.get_instance()
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Show config if verbose
    if verbose and not quiet:
        masked_url = config._mask_database_password(config.database_url)
        console.print(f"[bold blue]Database URL:[/] {masked_url}")

    try:
        ***REMOVED*** Get engine and applied migrations
        engine = get_engine(database_url, config)
        applied_migrations = get_applied_migrations(engine)

        if not applied_migrations:
            console.print("[bold blue]ℹ[/] No migrations to downgrade!")
            return 0

        ***REMOVED*** Sort migration IDs for processing
        migration_ids = sorted(applied_migrations.keys())

        ***REMOVED*** Determine migrations to downgrade
        if all_migrations:
            migrations_to_downgrade = list(reversed(migration_ids))
            operation_desc = "all migrations"
        elif target:
            ***REMOVED*** Find target migration in applied list
            if target not in migration_ids:
                console.print(
                    f"[bold red]❌ Target migration '{target}' not found in applied migrations!"
                )
                return 1
            target_index = migration_ids.index(target)
            migrations_to_downgrade = list(reversed(migration_ids[target_index:]))
            operation_desc = f"migrations from {target} onwards"
        else:
            ***REMOVED*** Downgrade specified number of steps
            migrations_to_downgrade = list(reversed(migration_ids[-steps:]))
            operation_desc = f"{steps} migration(s)"

        if not migrations_to_downgrade:
            console.print("[bold blue]ℹ[/] No migrations to downgrade!")
            return 0

        ***REMOVED*** Show what will be downgraded
        if not quiet:
            table = Table(title="Migrations to Downgrade")
            table.add_column("Migration ID", style="cyan")
            table.add_column("Description", style="yellow")
            table.add_column("Order", style="green")

            for i, migration_id in enumerate(migrations_to_downgrade):
                description = applied_migrations.get(migration_id, "No description")
                table.add_row(migration_id, description, str(i + 1))

            console.print(table)

        ***REMOVED*** Confirm downgrade
        if confirm:
            console.print(f"[bold yellow]⚠️  About to downgrade {operation_desc}!")
            if not typer.confirm("Are you sure you want to proceed?"):
                console.print("Downgrade cancelled.")
                return 0

        ***REMOVED*** Perform downgrades
        downgraded_count = 0
        for migration_id in migrations_to_downgrade:
            if not quiet:
                console.print(f"[bold blue]Downgrading migration: {migration_id}[/]")

            success = _downgrade_single_migration(
                engine, migration_id, applied_migrations[migration_id], verbose, quiet
            )
            if success:
                downgraded_count += 1
            else:
                console.print(f"[bold red]❌ Failed to downgrade migration: {migration_id}[/]")
                break

        ***REMOVED*** Show results
        if not quiet:
            if downgraded_count > 0:
                console.print(
                    f"[bold green]✓[/] Successfully downgraded {downgraded_count} migrations!"
                )
            else:
                console.print("[bold red]❌ No migrations were downgraded!")

        return 0 if downgraded_count > 0 else 1

    except Exception as e:
        error_msg = f"Error during downgrade: {str(e)}"
        console.print(f"[bold red]❌ {error_msg}[/]")
        logger.error(error_msg)
        return 1


def _downgrade_single_migration(
    engine: Engine,
    migration_id: str,
    migration_desc: str,
    verbose: bool,
    quiet: bool,
) -> bool:
    """Downgrade a single migration.

    Args:
        engine: SQLAlchemy engine
        migration_id: Migration ID to downgrade
        migration_desc: Migration description
        verbose: Enable verbose output
        quiet: Suppress output

    Returns:
        True if successful, False otherwise
    """
    logger = get_logger(__name__)

    ***REMOVED*** Show progress if not quiet
    if not quiet:
        console.print(f"[bold yellow]⟳[/] Downgrading: {migration_id}")

    ***REMOVED*** Import the migration module
    try:
        module = importlib.import_module(f"backend_api.db.migrations.{migration_id}")
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


***REMOVED*** ============================================================================
***REMOVED*** Database Teardown (Development Only)
***REMOVED*** ============================================================================


@app.command("teardown")
def teardown_database(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    log_level: str = typer.Option("INFO", help="Logging level", show_default=True),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
    database_url: Optional[str] = typer.Option(None, help="Database URL (overrides config)"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Confirm before teardown"),
    force: bool = typer.Option(False, "--force", help="Force teardown in production (dangerous!)"),
) -> int:
    """Teardown database (DEVELOPMENT ONLY - destroys all data!)."""
    ***REMOVED*** Configure logging
    configure_logging(log_level=log_level, verbose=verbose, quiet=quiet)
    logger = get_logger(__name__)

    ***REMOVED*** Get configuration
    config = Config.get_instance()
    if database_url:
        config.database_url = database_url

    ***REMOVED*** Safety check for production
    if config.environment == "production" and not force:
        console.print(
            "[bold red]❌ Teardown is not allowed in production environment![/]\n"
            "[dim]Use --force flag if you really know what you're doing.[/dim]"
        )
        return 1

    ***REMOVED*** Show config if verbose
    if verbose and not quiet:
        masked_url = config._mask_database_password(config.database_url)
        console.print(f"[bold blue]Database URL:[/] {masked_url}")

    ***REMOVED*** Warning message
    if not quiet:
        console.print(
            Panel(
                "[bold red]⚠️  WARNING: This will destroy ALL data in the database![/]\n\n"
                "This operation will:\n"
                "• Drop all tables\n"
                "• Remove all data\n"
                "• Reset the database to empty state\n\n"
                "[bold yellow]This action cannot be undone![/]",
                title="Database Teardown",
                border_style="red",
            )
        )

    ***REMOVED*** Confirm teardown
    if confirm:
        console.print(f"[bold red]Environment: {config.environment}[/]")
        if not typer.confirm("Are you absolutely sure you want to proceed with teardown?"):
            console.print("Teardown cancelled.")
            return 0

        ***REMOVED*** Double confirmation for production
        if config.environment == "production":
            console.print("[bold red]This is a PRODUCTION environment![/]")
            if not typer.confirm("Type 'yes' to confirm production teardown", default=False):
                console.print("Teardown cancelled.")
                return 0

    try:
        ***REMOVED*** Import here to avoid circular imports
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError

        ***REMOVED*** Create engine
        engine = create_engine(config.database_url)

        with console.status("[bold red]Tearing down database...[/]"):
            with engine.connect() as conn:
                ***REMOVED*** Start transaction
                trans = conn.begin()

                try:
                    ***REMOVED*** Drop all tables (cascade to handle foreign keys)
                    conn.execute(text("DROP SCHEMA public CASCADE"))
                    conn.execute(text("CREATE SCHEMA public"))
                    conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
                    conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

                    ***REMOVED*** Commit transaction
                    trans.commit()

                except Exception as e:
                    ***REMOVED*** Rollback on error
                    trans.rollback()
                    raise e

        ***REMOVED*** Show results
        if not quiet:
            console.print("[bold green]✓[/] Database teardown completed successfully!")
            console.print(
                "[dim]You may want to run 'db database init --create-tables' to recreate the schema.[/dim]"
            )

        logger.info("Database teardown completed successfully")
        return 0

    except SQLAlchemyError as e:
        error_msg = f"Database error during teardown: {str(e)}"
        console.print(f"[bold red]❌ {error_msg}[/]")
        logger.error(error_msg)
        return 1
    except Exception as e:
        error_msg = f"Unexpected error during teardown: {str(e)}"
        console.print(f"[bold red]❌ {error_msg}[/]")
        logger.error(error_msg)
        return 1


***REMOVED*** Register database commands directly with db_app (not as a nested group)
from backend_api.cli import db_app

***REMOVED*** Register each command directly
db_app.command("init")(init_database)
db_app.command("migrate")(migrate_database)
db_app.command("downgrade")(downgrade_database)
db_app.command("teardown")(teardown_database)
