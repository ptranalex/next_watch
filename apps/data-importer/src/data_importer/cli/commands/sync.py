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
from data_importer.config.app import DEFAULT_TMDB_ACCESS_TOKEN, DEFAULT_OMDB_API_KEY, Config

console = Console()
logger = logging.getLogger(__name__)

app = typer.Typer(name="sync", help="Sync movie and TV data from external sources.")


@app.command(name="movies")
@with_logging(log_level="INFO")
def sync_movies(
    start_year: Optional[int] = typer.Option(
        None, "--start-year", "-s", help="Starting year (inclusive), defaults to config value"
    ),
    end_year: Optional[int] = typer.Option(
        None, "--end-year", "-e", help="Ending year (inclusive), defaults to config value"
    ),
    limit_per_year: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum movies per year, defaults to config value"
    ),
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
    save_to_db: Optional[bool] = typer.Option(
        None, "--save/--no-save", help="Save movies to database, defaults to config value"
    ),
    include_credits: Optional[bool] = typer.Option(
        None,
        "--credits/--no-credits",
        help="Include cast and crew information, defaults to config value",
    ),
    sort_by: Optional[str] = typer.Option(
        None,
        "--sort-by",
        help="How to sort movies: 'popularity.desc' or 'vote_count.desc', defaults to config value",
    ),
    min_vote_count: Optional[int] = typer.Option(
        None,
        "--min-votes",
        help="Minimum number of votes for movies to include, defaults to config value",
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
        data-importer sync movies --start-year 2022 --end-year 2023 --credits --save
        data-importer sync movies --start-year 2010 --end-year 2010 --limit 5 --no-save --verbose
    """
    ***REMOVED*** Get configuration instance
    config = Config.get_instance()

    ***REMOVED*** Use config values if not specified
    actual_start_year = start_year if start_year is not None else config.movie_sync_start_year
    actual_end_year = end_year if end_year is not None else config.movie_sync_end_year
    actual_limit = (
        limit_per_year if limit_per_year is not None else config.movie_sync_limit_per_year
    )
    actual_save_to_db = save_to_db if save_to_db is not None else config.movie_sync_save_to_db
    actual_include_credits = (
        include_credits if include_credits is not None else config.movie_sync_include_credits
    )
    actual_sort_by = sort_by if sort_by is not None else config.movie_sync_sort_by
    actual_min_vote_count = (
        min_vote_count if min_vote_count is not None else config.movie_sync_min_vote_count
    )

    ***REMOVED*** Display configuration if verbose
    if verbose:
        console.print("[bold cyan]Movie Sync Configuration:[/bold cyan]")
        console.print(f"Year range: {actual_start_year} to {actual_end_year}")
        console.print(f"Limit per year: {actual_limit}")
        console.print(f"Sort by: {actual_sort_by}")
        console.print(f"Min vote count: {actual_min_vote_count}")
        console.print(f"Include credits: {actual_include_credits}")
        console.print(f"Save to database: {actual_save_to_db}")
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
    if actual_save_to_db:
        engine = get_engine()
        db_session = Session(engine)

    console.print(
        f"[cyan]Starting movie sync for years {actual_start_year}-{actual_end_year}...[/cyan]"
    )
    if actual_include_credits:
        console.print("[cyan]Including cast and crew information[/cyan]")

    try:
        ***REMOVED*** Run the sync operation
        results = asyncio.run(
            sync_movies_by_year_range(
                tmdb_client=tmdb_client,
                omdb_client=omdb_client,
                start_year=actual_start_year,
                end_year=actual_end_year,
                limit_per_year=actual_limit,
                show_progress=True,
                db_session=db_session,
                save_to_db=actual_save_to_db,
                include_credits=actual_include_credits,
                sort_by=actual_sort_by,
                min_vote_count=actual_min_vote_count,
            )
        )

        ***REMOVED*** Calculate end time and duration
        end_time = datetime.now()
        results["end_time"] = end_time.isoformat()

        ***REMOVED*** Display formatted results
        formatted_results = format_sync_results(results)
        console.print(formatted_results)

        if actual_include_credits:
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
