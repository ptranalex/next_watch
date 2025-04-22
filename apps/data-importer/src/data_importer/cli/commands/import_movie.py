"""Command for importing movies from TMDB."""

import os
import logging
import asyncio
from typing import Optional, List
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import Session

from movie_storage.db.db import get_engine, get_session
from data_importer.services import TMDBClient, TMDBDataAdapter

console = Console()
logger = logging.getLogger(__name__)

app = typer.Typer(name="movie", help="Import movie data from TMDB.")


@app.command(name="id")
def import_by_id(
    movie_id: int = typer.Argument(..., help="TMDB movie ID to import"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="TMDB API key", envvar="TMDB_API_KEY"
    ),
    language: str = typer.Option("en-US", "--language", "-l", help="Language for movie data"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Import a specific movie by its TMDB ID."""
    ***REMOVED*** Display configuration
    if verbose:
        console.print("[bold]Configuration:[/bold]")
        console.print(f"Movie ID: {movie_id}")
        console.print(f"Language: {language}")
        console.print(f"API Key: {'Provided' if api_key else 'Not provided'}")
        console.print()

    ***REMOVED*** Ensure we have an API key
    if not api_key:
        api_key = os.environ.get("TMDB_API_KEY")
        if not api_key:
            console.print("[bold red]Error:[/bold red] TMDB API key is required.")
            console.print("Provide it via --api-key or set the TMDB_API_KEY environment variable.")
            raise typer.Exit(code=1)

    ***REMOVED*** Initialize clients
    tmdb_client = TMDBClient(access_token=api_key)
    data_adapter = TMDBDataAdapter(tmdb_client)

    ***REMOVED*** Setup database
    engine = get_engine()

    ***REMOVED*** Import the movie
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Importing movie...[/bold green]"),
        transient=True,
    ) as progress:
        progress.add_task("import", total=None)

        try:
            ***REMOVED*** Run the import
            result = asyncio.run(_import_movie(data_adapter, movie_id, language))

            if not result:
                console.print(f"[bold red]Failed to import movie ID {movie_id}[/bold red]")
                raise typer.Exit(code=1)

            ***REMOVED*** Display result
            console.print("[bold green]Movie imported successfully![/bold green]")
            console.print(f"Title: {result['title']}")
            console.print(f"Database ID: {result['movie_id']}")
            console.print(f"Credits imported: {result['credit_count']}")
            console.print(f"Operation: {result['operation']}")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(code=1)
        finally:
            asyncio.run(tmdb_client.close())


@app.command(name="popular")
def import_popular(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of movies to import"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="TMDB API key", envvar="TMDB_API_KEY"
    ),
    language: str = typer.Option("en-US", "--language", "-l", help="Language for movie data"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Import popular movies from TMDB."""
    ***REMOVED*** Display configuration
    if verbose:
        console.print("[bold]Configuration:[/bold]")
        console.print(f"Limit: {limit}")
        console.print(f"Language: {language}")
        console.print(f"API Key: {'Provided' if api_key else 'Not provided'}")
        console.print()

    ***REMOVED*** Ensure we have an API key
    if not api_key:
        api_key = os.environ.get("TMDB_API_KEY")
        if not api_key:
            console.print("[bold red]Error:[/bold red] TMDB API key is required.")
            console.print("Provide it via --api-key or set the TMDB_API_KEY environment variable.")
            raise typer.Exit(code=1)

    ***REMOVED*** Initialize clients
    tmdb_client = TMDBClient(access_token=api_key)
    data_adapter = TMDBDataAdapter(tmdb_client)

    ***REMOVED*** Import popular movies
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Importing popular movies...[/bold green]"),
        transient=True,
    ) as progress:
        progress.add_task("import", total=None)

        try:
            ***REMOVED*** Run the import
            results = asyncio.run(_import_popular_movies(data_adapter, limit, language))

            if not results:
                console.print("[bold yellow]No movies were imported[/bold yellow]")
                raise typer.Exit(code=0)

            ***REMOVED*** Display results table
            table = Table(title=f"Imported {len(results)} Popular Movies")
            table.add_column("ID", justify="right")
            table.add_column("TMDB ID", justify="right")
            table.add_column("Title")
            table.add_column("Credits", justify="right")
            table.add_column("Operation")

            for result in results:
                table.add_row(
                    str(result["movie_id"]),
                    str(result["tmdb_id"]),
                    result["title"],
                    str(result["credit_count"]),
                    result["operation"],
                )

            console.print(table)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(code=1)
        finally:
            asyncio.run(tmdb_client.close())


async def _import_movie(
    data_adapter: TMDBDataAdapter, movie_id: int, language: str
) -> Optional[dict]:
    """Helper function to import a movie asynchronously."""
    engine = get_engine()
    session = Session(engine)
    try:
        return await data_adapter.import_movie_by_id(session, movie_id, language)
    finally:
        session.close()


async def _import_popular_movies(
    data_adapter: TMDBDataAdapter, limit: int, language: str
) -> List[dict]:
    """Helper function to import popular movies asynchronously."""
    engine = get_engine()
    session = Session(engine)
    try:
        return await data_adapter.import_popular_movies(session, limit, language)
    finally:
        session.close()
