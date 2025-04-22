"""TMDB data adapter service.

This module provides the bridge between the TMDB API client and the movie_storage
operations, handling the conversion of API responses to database models.
"""

import logging
from typing import Dict, Any, Optional, List

from sqlmodel import Session

from movie_storage.db.operations.movie import create_movie_from_tmdb_details
from movie_storage.db.operations import (
    get_movie_by_tmdb_id,
)

from data_importer.services.tmdb import TMDBClient

logger = logging.getLogger(__name__)


class TMDBDataAdapter:
    """Adapter for importing data from TMDB API into the movie storage database."""

    def __init__(self, tmdb_client: TMDBClient):
        """Initialize the TMDB data adapter.

        Args:
            tmdb_client: An initialized TMDBClient instance
        """
        self.tmdb_client = tmdb_client

    async def import_movie_by_id(
        self, session: Session, movie_id: int, language: str = "en-US"
    ) -> Optional[Dict[str, Any]]:
        """Import a movie by its TMDB ID.

        This method fetches movie details with credits from the TMDB API
        and creates or updates the corresponding records in the database.

        Args:
            session: Database session
            movie_id: TMDB movie ID
            language: Language for movie data (default: "en-US")

        Returns:
            Dictionary with import result information, or None if import failed
        """
        try:
            ***REMOVED*** Check if movie already exists in database
            existing_movie = get_movie_by_tmdb_id(session, movie_id)

            ***REMOVED*** Fetch movie details with credits
            movie_details = await self.tmdb_client.get_movie_details(
                movie_id=movie_id, language=language, append_credits=True
            )

            if not movie_details:
                logger.error(f"Failed to fetch movie details for ID {movie_id}")
                return None

            ***REMOVED*** Ensure language is not None to prevent SQL errors
            if movie_details.get("language") is None:
                movie_details["language"] = language.split("-")[0] if "-" in language else language

            ***REMOVED*** Create or update movie in database
            db_movie = create_movie_from_tmdb_details(session, movie_details)

            result = {
                "movie_id": db_movie.id,
                "tmdb_id": db_movie.tmdb_id,
                "title": db_movie.title,
                "credit_count": len(db_movie.credits) if db_movie.credits else 0,
                "operation": "updated" if existing_movie else "created",
            }

            logger.info(
                f"Successfully {'updated' if existing_movie else 'imported'} "
                f"movie: {db_movie.title} (ID: {db_movie.id}, TMDB ID: {db_movie.tmdb_id})"
            )

            return result

        except Exception as e:
            logger.exception(f"Error importing movie ID {movie_id}: {str(e)}")
            return None

    async def import_popular_movies(
        self, session: Session, limit: int = 10, language: str = "en-US"
    ) -> List[Dict[str, Any]]:
        """Import popular movies from TMDB.

        Args:
            session: Database session
            limit: Maximum number of movies to import (default: 10)
            language: Language for movie data (default: "en-US")

        Returns:
            List of import result dictionaries
        """
        results = []

        try:
            ***REMOVED*** Get popular movies list
            popular_movies = await self.tmdb_client.get_popular_movies()

            ***REMOVED*** Import each movie up to the limit
            for i, movie_data in enumerate(popular_movies[:limit]):
                movie_id = movie_data.get("id")
                if not movie_id:
                    continue

                result = await self.import_movie_by_id(session, movie_id, language)

                if result:
                    results.append(result)

            logger.info(f"Imported {len(results)} popular movies")

        except Exception as e:
            logger.exception(f"Error importing popular movies: {str(e)}")

        return results
