"""Command for syncing movies from external sources."""

import os
import logging
import asyncio
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from sqlmodel import Session

from movie_storage.db.db import get_engine
from data_importer.config.logging import with_logging
from data_importer.services.tmdb import TMDBClient
from data_importer.services.omdb import OMDBClient
from data_importer.sync.movie_sync import sync_movies_by_year_range, format_sync_results
from data_importer.cli.utils import get_api_key
from data_importer.config.app import DEFAULT_TMDB_ACCESS_TOKEN, DEFAULT_OMDB_API_KEY

console = Console()
logger = logging.getLogger(__name__)

app = typer.Typer(name="sync", help="Sync movie and TV data from external sources.")


@app.command(name="movies")
@with_logging(log_level="INFO")
def sync_movies(
    start_year: int = typer.Argument(..., help="Starting year (inclusive)"),
    end_year: int = typer.Argument(..., help="Ending year (inclusive)"),
    limit_per_year: int = typer.Option(20, "--limit", "-l", help="Maximum movies per year"),
    tmdb_access_token: Optional[str] = typer.Option(
        DEFAULT_TMDB_ACCESS_TOKEN,
        "--tmdb-token",
        "-t",
        help="TMDB Bearer token (or set TMDB_ACCESS_TOKEN environment variable)",
    ),
    omdb_api_key: Optional[str] = typer.Option(
        DEFAULT_OMDB_API_KEY,
        "--omdb-key",
        "-o",
        help="OMDB API key (or set OMDB_API_KEY environment variable)",
    ),
    save_to_db: bool = typer.Option(False, "--save/--no-save", help="Save movies to database"),
    include_credits: bool = typer.Option(
        False, "--credits/--no-credits", help="Include cast and crew information"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Sync movies from TMDB and OMDB for a range of years.

    This command fetches movie data from external sources and optionally
    saves it to the database. With the --credits flag, it will also fetch
    and save cast and crew information.

    API Keys:
        - TMDB: Get from https://www.themoviedb.org/settings/api
        - OMDB: Get from https://www.omdbapi.com/apikey.aspx

    Examples:
        data-importer sync movies 2022 2023 --credits --save
        data-importer sync movies 2010 2010 --limit 5 --no-save --verbose
    """
    ***REMOVED*** Display configuration if verbose
    if verbose:
        console.print("[bold]Configuration:[/bold]")
        console.print(f"Year range: {start_year} to {end_year}")
        console.print(f"Limit per year: {limit_per_year}")
        console.print(f"Save to database: {save_to_db}")
        console.print(f"Include credits: {include_credits}")
        console.print(f"TMDB token: {'Provided' if tmdb_access_token else 'Not provided'}")
        console.print(f"OMDB API key: {'Provided' if omdb_api_key else 'Not provided'}")
        console.print()

    ***REMOVED*** Get API keys using the standardized utility
    tmdb_access_token = get_api_key(
        tmdb_access_token, "TMDB_ACCESS_TOKEN", "TMDB access token", console, required=True
    )
    omdb_api_key = get_api_key(omdb_api_key, "OMDB_API_KEY", "OMDB API key", console, required=True)

    ***REMOVED*** Initialize clients
    tmdb_client = TMDBClient(access_token=tmdb_access_token)
    omdb_client = OMDBClient(api_key=omdb_api_key)

    ***REMOVED*** Prepare database session if saving to database
    db_session = None
    if save_to_db:
        engine = get_engine()
        db_session = Session(engine)

    console.print(f"[cyan]Starting movie sync for years {start_year}-{end_year}...[/cyan]")
    if include_credits:
        console.print("[cyan]Including cast and crew information[/cyan]")

    try:
        ***REMOVED*** Run the sync operation
        results = asyncio.run(
            sync_movies_by_year_range(
                tmdb_client=tmdb_client,
                omdb_client=omdb_client,
                start_year=start_year,
                end_year=end_year,
                limit_per_year=limit_per_year,
                show_progress=True,
                db_session=db_session,
                save_to_db=save_to_db,
                include_credits=include_credits,
            )
        )

        ***REMOVED*** Calculate end time and duration
        end_time = datetime.now()
        results["end_time"] = end_time.isoformat()

        ***REMOVED*** Display formatted results
        formatted_results = format_sync_results(results)
        console.print(formatted_results)

        if include_credits:
            credits_saved = results.get("credits_saved", 0)
            if credits_saved > 0:
                console.print(f"[green]\nSaved {credits_saved} cast and crew credits[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error during movie sync")
        raise typer.Exit(code=1)
    finally:
        ***REMOVED*** Clean up resources
        if db_session:
            db_session.close()
        asyncio.run(tmdb_client.close())
        asyncio.run(omdb_client.close())
