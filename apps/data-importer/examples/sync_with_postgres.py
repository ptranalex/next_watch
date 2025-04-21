***REMOVED***!/usr/bin/env python3
"""Example script demonstrating movie synchronization with PostgreSQL database."""

import asyncio
import logging
import os
from pathlib import Path

from rich.console import Console
from sqlmodel import Session, select

from data_importer.services import TMDBClient, OMDBClient
from data_importer.sync.movie_sync import sync_movies_by_year_range, format_sync_results
from movie_storage.utils import setup_movie_storage  ***REMOVED*** type: ignore
from movie_storage.movie_operations import get_movies  ***REMOVED*** type: ignore
from movie_schema.models import Movie  ***REMOVED*** type: ignore

***REMOVED*** Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
console = Console()

***REMOVED*** API keys (should be loaded from environment variables or config file)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "your_tmdb_api_key")
OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "your_omdb_api_key")


async def main():
    """Run the example movie sync with PostgreSQL database storage."""
    ***REMOVED*** Initialize clients
    tmdb_client = TMDBClient(api_key=TMDB_API_KEY)
    omdb_client = OMDBClient(api_key=OMDB_API_KEY)

    ***REMOVED*** Setup movie storage with PostgreSQL configuration
    ***REMOVED*** The config is loaded from .env.local automatically
    setup_info = setup_movie_storage(create_tables=True, verbose=True)

    ***REMOVED*** Log the database URL being used (with password masked)
    db_url = setup_info["database_url"]
    console.print(f"[bold]Using database:[/bold] {db_url}")

    ***REMOVED*** Define sync parameters
    start_year = 2022
    end_year = 2022  ***REMOVED*** Just sync one year for testing
    limit_per_year = 5  ***REMOVED*** Just 5 movies for quick testing

    console.print(
        f"[bold green]Starting movie sync for years {start_year}-{end_year}[/bold green]"
    )

    ***REMOVED*** Create a database session
    from sqlmodel import create_engine

    engine = create_engine(db_url)

    with Session(engine) as session:
        ***REMOVED*** Perform sync with database storage ENABLED
        results = await sync_movies_by_year_range(
            tmdb_client=tmdb_client,
            omdb_client=omdb_client,
            start_year=start_year,
            end_year=end_year,
            limit_per_year=limit_per_year,
            show_progress=True,
            db_session=session,
            save_to_db=True,  ***REMOVED*** IMPORTANT: Enable database storage
        )

        ***REMOVED*** Format and display results
        formatted_results = format_sync_results(results)
        console.print(formatted_results)

        ***REMOVED*** Verify movies were saved to database
        console.print("\n[bold yellow]Verifying movies in database...[/bold yellow]")
        movies = get_movies(session, limit=10)

        if movies:
            console.print(
                f"[green]Successfully found {len(movies)} movies in the database:[/green]"
            )
            for i, movie in enumerate(movies, 1):
                console.print(f"  {i}. {movie.title} (TMDB ID: {movie.tmdb_id})")
        else:
            console.print("[red]No movies found in database![/red]")


if __name__ == "__main__":
    asyncio.run(main())
