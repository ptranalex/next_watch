"""
Database setup and migration script.
"""

import os

import typer
from movie_storage.db import init_db
from movie_storage.db.migrations import run_migration
from movie_storage.utils import setup_movie_storage

app = typer.Typer()

***REMOVED*** Database URL from environment variable with a PostgreSQL default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://alex:postgres@localhost:5432/next_watch")


@app.command()
def initialize_db(create_tables: bool = False):
    """
    Initialize the database connection.

    Args:
        create_tables: Whether to create tables in the database
    """
    typer.echo(f"Initializing database connection to: {DATABASE_URL}")
    init_db(DATABASE_URL, create_tables=create_tables)
    typer.echo("Database connection initialized successfully!")


@app.command()
def run_migrations():
    """
    Run database migrations using Alembic.
    """
    typer.echo("Running database migrations...")
    run_migration(DATABASE_URL)
    typer.echo("Migrations completed successfully!")


@app.command()
def setup_storage():
    """
    Setup movie storage with initial configuration.

    This will initialize the database and create any necessary tables.
    """
    typer.echo("Setting up movie storage...")
    setup_movie_storage(database_url=DATABASE_URL, create_tables=True)
    typer.echo("Movie storage setup completed!")


if __name__ == "__main__":
    app()
