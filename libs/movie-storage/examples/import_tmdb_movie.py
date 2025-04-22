***REMOVED***!/usr/bin/env python3
"""Example script to import a movie from TMDB API into the database."""

import json
import sys
import logging
import argparse
from pathlib import Path

from sqlmodel import Session

from movie_storage.config.logging import with_logging
from movie_storage.config.app import Config
from movie_storage.db.db import init_db, get_engine
from movie_storage.db.operations.movie import create_movie_from_tmdb_details

***REMOVED*** Configure logging
logger = logging.getLogger(__name__)


@with_logging(log_level="INFO", verbose=True)
def import_tmdb_movie(json_file: Path, create_tables: bool = False) -> None:
    """Import a movie from a TMDB API JSON response file.

    Args:
        json_file: Path to the JSON file containing TMDB movie details
        create_tables: Whether to create tables if they don't exist
    """
    logger.info(f"Importing movie data from {json_file}")

    ***REMOVED*** Load movie data from JSON file
    with open(json_file, "r") as f:
        tmdb_data = json.load(f)

    ***REMOVED*** Initialize the database
    config = Config.get_instance()
    init_db(create_tables=create_tables)
    engine = get_engine()

    ***REMOVED*** Create a database session
    with Session(engine) as session:
        ***REMOVED*** Import the movie
        movie = create_movie_from_tmdb_details(session, tmdb_data)

        ***REMOVED*** Print the imported movie details
        logger.info(f"Successfully imported movie: {movie.title} (ID: {movie.id})")
        logger.info(f"  TMDB ID: {movie.tmdb_id}")
        logger.info(f"  IMDb ID: {movie.imdb_id}")
        logger.info(f"  Release Date: {movie.release_date}")
        logger.info(f"  Runtime: {movie.runtime} minutes")
        logger.info(f"  Vote Average: {movie.vote_average}")

        ***REMOVED*** Print genres
        if movie.genres:
            genre_names = [genre.name for genre in movie.genres]
            logger.info(f"  Genres: {', '.join(genre_names)}")

        ***REMOVED*** Print credits
        if movie.credits:
            logger.info(f"  Cast: {len(movie.credits)} actors")
            for i, credit in enumerate(
                sorted(movie.credits, key=lambda c: c.order or 999)[:5], 1
            ):
                logger.info(f"    {i}. {credit.name} as {credit.character}")

            if len(movie.credits) > 5:
                logger.info(f"    ... and {len(movie.credits) - 5} more")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import a movie from TMDB API JSON file"
    )
    parser.add_argument(
        "json_file", type=Path, help="Path to the TMDB API JSON response file"
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create database tables if they don't exist",
    )

    args = parser.parse_args()

    if not args.json_file.exists():
        print(f"Error: File {args.json_file} does not exist")
        return 1

    try:
        import_tmdb_movie(args.json_file, args.create_tables)
        return 0
    except Exception as e:
        logger.error(f"Error importing movie: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
