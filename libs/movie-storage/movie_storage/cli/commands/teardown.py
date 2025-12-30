"""Database teardown commands."""

import typer
from rich.console import Console
from rich.prompt import Confirm
from sqlalchemy import text
from sqlmodel import SQLModel

from movie_storage.cli import app as cli_app
from movie_storage.config.app import Config
from movie_storage.db.db import get_engine

# Create app for this command group
app = typer.Typer(help="Database teardown commands (DEVELOPMENT ONLY)")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    drop_all: bool = typer.Option(
        False, "--drop-all", help="Drop all tables (WARNING: Destructive operation)"
    ),
    clear: list[str] | None = typer.Option(
        None,
        "--clear",
        help="Clear specific tables",
        show_default=False,
    ),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm destructive operation"),
    database_url: str | None = typer.Option(None, help="Database URL (overrides config)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
) -> int:
    """Teardown database for development purposes."""
    if not confirm:
        console.print("[bold red]Error:[/] Teardown requires --confirm flag due to data loss risk")
        if not quiet:
            console.print("Run with --confirm to proceed with the teardown.")
        raise typer.Exit(code=1)

    if not drop_all and not clear:
        console.print("[bold red]Error:[/] No teardown action specified.")
        if not quiet:
            console.print("Use --drop-all or --clear")
        raise typer.Exit(code=1)

    # Get configuration
    config = Config.get_instance()
    if database_url:
        config.database_url = database_url

    # Show config if verbose
    if verbose and not quiet:
        masked_url = config._mask_database_password(config.database_url)
        console.print(f"[bold blue]Database URL:[/] {masked_url}")

    # Get engine
    engine = get_engine(database_url, config)

    # Drop all tables
    if drop_all:
        # Final confirmation for dropping all tables
        if not quiet and not Confirm.ask(
            "[bold red]Warning:[/] You are about to drop ALL tables from the database. This cannot be undone. Continue?"
        ):
            console.print("[bold yellow]Teardown cancelled.[/]")
            raise typer.Exit(code=1)

        if not quiet:
            console.print("[bold yellow]Dropping all tables from database...[/]")

        with console.status("Dropping tables..."):
            SQLModel.metadata.drop_all(engine)

        if not quiet:
            console.print("[bold green]✓[/] All tables dropped successfully!")

        return 0

    # Clear specific tables
    if clear:
        valid_tables = {"movies", "genres", "migrations", "credits"}
        invalid_tables = set(clear) - valid_tables

        if invalid_tables:
            console.print(f"[bold red]Error:[/] Invalid table(s): {', '.join(invalid_tables)}")
            if not quiet:
                console.print(f"Valid tables: {', '.join(valid_tables)}")
            raise typer.Exit(code=1)

        if not quiet:
            console.print(f"[bold yellow]Clearing tables: {', '.join(clear)}[/]")

        with engine.begin() as conn:
            if "movies" in clear:
                if not quiet:
                    console.print("Clearing movie_genrelink table...")
                conn.execute(text("DELETE FROM moviegenrelink"))

                if not quiet:
                    console.print("Clearing credit table...")
                conn.execute(text("DELETE FROM credit"))

                if not quiet:
                    console.print("Clearing movie table...")
                conn.execute(text("DELETE FROM movie"))

            if "genres" in clear:
                if "movies" not in clear:
                    if not quiet:
                        console.print("Clearing movie_genrelink table...")
                    conn.execute(text("DELETE FROM moviegenrelink"))

                if not quiet:
                    console.print("Clearing genre table...")
                conn.execute(text("DELETE FROM genre"))

            if "migrations" in clear:
                if not quiet:
                    console.print("Clearing migrations table...")
                conn.execute(text("DELETE FROM migrations"))

            if "credits" in clear and "movies" not in clear:
                if not quiet:
                    console.print("Clearing credit table...")
                conn.execute(text("DELETE FROM credit"))

        if not quiet:
            console.print(f"[bold green]✓[/] Cleared tables: {', '.join(clear)}")

    return 0


# Register with parent app
cli_app.add_typer(app, name="teardown")
