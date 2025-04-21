***REMOVED***!/usr/bin/env python3
"""Example of using the with_logging decorator.

This example demonstrates how to use the with_logging decorator to
automatically configure logging for a function.
"""

import logging
import asyncio
from pathlib import Path

from data_importer.config import with_logging, DEFAULT_LOGS_DIR
from data_importer.services import TMDBClient, OMDBClient
from data_importer.sync.movie_sync import sync_movies_by_year_range, format_sync_results

***REMOVED*** Get a logger for this module
logger = logging.getLogger(__name__)


@with_logging(log_level="DEBUG", log_dir=DEFAULT_LOGS_DIR, verbose=True)
async def run_movie_sync_example():
    """Run a movie sync example with logging."""
    logger.info("Starting movie sync example")

    ***REMOVED*** Create API clients
    tmdb_client = TMDBClient()
    omdb_client = OMDBClient()

    ***REMOVED*** Sync movies for a single year
    start_year = 2020
    end_year = 2020
    limit = 5

    logger.info(f"Syncing movies from {start_year} to {end_year}, limit: {limit}")

    ***REMOVED*** Call the decorated sync function
    results = await sync_movies_by_year_range(
        tmdb_client=tmdb_client,
        omdb_client=omdb_client,
        start_year=start_year,
        end_year=end_year,
        limit_per_year=limit,
        show_progress=True,
        save_to_db=False,
    )

    ***REMOVED*** Format and print results
    formatted_results = format_sync_results(results)
    logger.info("Sync complete")
    print("\n" + formatted_results)


@with_logging(log_level="INFO", verbose=False)
def main():
    """Main entry point for the example."""
    logger.info("Starting example")
    asyncio.run(run_movie_sync_example())
    logger.info("Example complete")


if __name__ == "__main__":
    main()
