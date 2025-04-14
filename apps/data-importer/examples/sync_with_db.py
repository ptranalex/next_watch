***REMOVED***!/usr/bin/env python3
"""Example script demonstrating movie synchronization with database storage."""

import asyncio
import logging
import os
from datetime import datetime

from rich.console import Console
from sqlmodel import Session

from data_importer.services import TMDBClient, OMDBClient
from data_importer.sync.movie_sync import sync_movies_by_year_range, format_sync_results
from movie_storage.db import init_db  ***REMOVED*** type: ignore

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
    """Run the example movie sync with database storage."""
    ***REMOVED*** Initialize clients
    tmdb_client = TMDBClient(api_key=TMDB_API_KEY)
    omdb_client = OMDBClient(api_key=OMDB_API_KEY)

    ***REMOVED*** Database setup
    db_url = "sqlite:///movies.db"
    init_db(db_url, create_tables=True)

    ***REMOVED*** Define sync parameters
    start_year = 2020
    end_year = 2021
    limit_per_year = 5  ***REMOVED*** Low number for demonstration

    console.print(
        f"[bold green]Starting movie sync for years {start_year}-{end_year}[/bold green]"
    )
    console.print(f"Each movie will be saved to the database at: {db_url}")

    ***REMOVED*** Create a database session
    from sqlmodel import create_engine

    engine = create_engine(db_url)

    with Session(engine) as session:
        ***REMOVED*** Perform sync with database storage
        results = await sync_movies_by_year_range(
            tmdb_client=tmdb_client,
            omdb_client=omdb_client,
            start_year=start_year,
            end_year=end_year,
            limit_per_year=limit_per_year,
            show_progress=True,
            db_session=session,
            save_to_db=True,
        )

        ***REMOVED*** Format and display results
        formatted_results = format_sync_results(results)
        console.print(formatted_results)


if __name__ == "__main__":
    asyncio.run(main())
