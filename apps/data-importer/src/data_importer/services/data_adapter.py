"""Data adapter services for movie APIs.

This module provides the bridge between external API clients and the movie_storage
operations, handling the conversion of API responses to database models.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

from sqlmodel import Session

from movie_storage.db.operations.movie import create_movie_from_tmdb_details
from movie_storage.db.operations import (
    get_movie_by_tmdb_id,
    get_movie_by_id,
    update_movie,
)

from data_importer.services.tmdb import TMDBClient
from data_importer.services.omdb import OMDBClient

logger = logging.getLogger(__name__)


class TMDBDataAdapter:
    """Adapter for importing data from TMDB API into the movie storage database."""

    def __init__(self, tmdb_client: TMDBClient):
        """Initialize the TMDB data adapter.

        Args:
            tmdb_client: An initialized TMDBClient instance
        """
        self.tmdb_client = tmdb_client

    def _extract_trailers(self, movie_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract trailer information from TMDB movie details.

        Args:
            movie_details: Movie details dictionary from TMDB

        Returns:
            List of trailer dictionaries with youtube_key, name, and is_official
        """
        trailers = []
        videos = movie_details.get("videos", {}).get("results", [])

        for video in videos:
            ***REMOVED*** Only include YouTube videos that are trailers
            if (
                video.get("site", "").lower() == "youtube"
                and video.get("type", "").lower() == "trailer"
            ):
                trailers.append(
                    {
                        "youtube_key": video.get("key"),
                        "name": video.get("name"),
                        "is_official": video.get("official", True),
                    }
                )

        return trailers

    async def import_movie_by_id(
        self,
        session: Session,
        movie_id: int,
        language: str = "en-US",
        include_credits: bool = True,
        include_videos: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Import a movie by its TMDB ID.

        This method fetches movie details with credits and videos from the TMDB API
        and creates or updates the corresponding records in the database.

        Args:
            session: Database session
            movie_id: TMDB movie ID
            language: Language for movie data (default: "en-US")
            include_credits: Whether to include credits information (default: True)
            include_videos: Whether to include video/trailer information (default: True)

        Returns:
            Dictionary with import result information, or None if import failed
        """
        try:
            ***REMOVED*** Check if movie already exists in database
            existing_movie = get_movie_by_tmdb_id(session, movie_id)

            ***REMOVED*** Fetch movie details with credits and videos
            movie_details = await self.tmdb_client.get_movie_details(
                movie_id=movie_id,
                language=language,
                append_credits=include_credits,
                append_videos=include_videos,
            )

            if not movie_details:
                logger.error(f"Failed to fetch movie details for ID {movie_id}")
                return None

            ***REMOVED*** Ensure language is not None to prevent SQL errors
            if movie_details.get("language") is None:
                movie_details["language"] = language.split("-")[0] if "-" in language else language

            ***REMOVED*** Extract trailers before creating movie
            trailers = self._extract_trailers(movie_details) if include_videos else []
            movie_details["trailers"] = trailers

            ***REMOVED*** Create or update movie in database
            db_movie = create_movie_from_tmdb_details(session, movie_details)

            result = {
                "movie_id": db_movie.id,
                "tmdb_id": db_movie.tmdb_id,
                "title": db_movie.title,
                "credit_count": len(db_movie.credits) if db_movie.credits else 0,
                "trailer_count": len(db_movie.trailers) if db_movie.trailers else 0,
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


class OMDBDataAdapter:
    """Adapter for enriching movie data from OMDB API."""

    def __init__(self, omdb_client: OMDBClient):
        """Initialize the OMDB data adapter.

        Args:
            omdb_client: An initialized OMDBClient instance
        """
        self.omdb_client = omdb_client

    async def get_movie_data(
        self, title: str, year: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get movie data from OMDB.

        Args:
            title: Movie title
            year: Optional release year

        Returns:
            Dictionary with normalized OMDB data or None if not found
        """
        try:
            ***REMOVED*** Search for movie in OMDB
            omdb_movie = await self.omdb_client.search_movie(title, year=year)

            if not omdb_movie or omdb_movie.get("Response") != "True":
                logger.debug(f"No OMDB data found for movie: {title} {f'({year})' if year else ''}")
                return None

            ***REMOVED*** Normalize OMDB data for our application
            normalized_data = {
                "imdb_id": omdb_movie.get("imdbID"),
                "imdb_rating": None,
                "runtime_mins": None,
                "plot": omdb_movie.get("Plot"),
                "actors": omdb_movie.get("Actors"),
                "director": omdb_movie.get("Director"),
                "awards": omdb_movie.get("Awards"),
                "metacritic_rating": None,
                "rotten_tomatoes_rating": None,
            }

            ***REMOVED*** Process IMDB rating
            if omdb_movie.get("imdbRating", "N/A") != "N/A":
                try:
                    normalized_data["imdb_rating"] = float(omdb_movie.get("imdbRating", 0))
                except (ValueError, TypeError):
                    pass

            ***REMOVED*** Process runtime
            runtime_str = omdb_movie.get("Runtime", "")
            if runtime_str and runtime_str != "N/A" and "min" in runtime_str:
                try:
                    normalized_data["runtime_mins"] = int(runtime_str.split()[0])
                except (ValueError, IndexError):
                    pass

            ***REMOVED*** Process Metascore
            if omdb_movie.get("Metascore", "N/A") != "N/A":
                try:
                    normalized_data["metacritic_rating"] = int(omdb_movie.get("Metascore", 0))
                except (ValueError, TypeError):
                    pass

            ***REMOVED*** Process Rotten Tomatoes rating from Ratings array
            ratings = omdb_movie.get("Ratings", [])
            for rating in ratings:
                if rating.get("Source") == "Rotten Tomatoes":
                    try:
                        ***REMOVED*** Remove % sign and convert to integer
                        rt_value = rating.get("Value", "").replace("%", "")
                        normalized_data["rotten_tomatoes_rating"] = int(rt_value)
                    except (ValueError, TypeError):
                        pass
                    break

            logger.debug(f"Retrieved OMDB data for movie: {title}")
            return normalized_data

        except Exception as e:
            logger.exception(f"Error getting OMDB data for {title}: {str(e)}")
            return None

    async def enrich_movie(
        self, session: Session, movie_id: int, title: str, year: Optional[str] = None
    ) -> bool:
        """Enrich an existing movie with OMDB data.

        Args:
            session: Database session
            movie_id: Database ID of the movie to enrich
            title: Movie title to search for in OMDB
            year: Optional release year

        Returns:
            True if movie was successfully enriched, False otherwise
        """
        try:
            ***REMOVED*** Get movie from database
            db_movie = get_movie_by_id(session, movie_id)
            if not db_movie:
                logger.warning(f"Movie with ID {movie_id} not found in database")
                return False

            ***REMOVED*** Get OMDB data
            omdb_data = await self.get_movie_data(title, year)
            if not omdb_data:
                return False

            ***REMOVED*** Only update fields that are not already populated
            updates = {}
            if not db_movie.imdb_id and omdb_data["imdb_id"]:
                updates["imdb_id"] = omdb_data["imdb_id"]
            if not db_movie.imdb_rating and omdb_data["imdb_rating"]:
                updates["imdb_rating"] = omdb_data["imdb_rating"]
            if not db_movie.runtime and omdb_data["runtime_mins"]:
                updates["runtime"] = omdb_data["runtime_mins"]
            if not db_movie.metacritic_rating and omdb_data["metacritic_rating"]:
                updates["metacritic_rating"] = omdb_data["metacritic_rating"]
            if not db_movie.rotten_tomatoes_rating and omdb_data["rotten_tomatoes_rating"]:
                updates["rotten_tomatoes_rating"] = omdb_data["rotten_tomatoes_rating"]
            if not db_movie.awards and omdb_data["awards"]:
                updates["awards"] = omdb_data["awards"]

            ***REMOVED*** Only update if we have changes
            if updates:
                update_movie(session, movie_id, updates)
                logger.info(f"Enriched movie with OMDB data: {db_movie.title}")
                return True
            else:
                logger.debug(f"No OMDB enrichment needed for: {db_movie.title}")
                return False

        except Exception as e:
            logger.exception(f"Error enriching movie ID {movie_id} with OMDB data: {str(e)}")
            return False


class MovieDataAdapter:
    """Combined adapter that uses both TMDB and OMDB for comprehensive movie data."""

    def __init__(self, tmdb_client: TMDBClient, omdb_client: OMDBClient):
        """Initialize the combined movie data adapter.

        Args:
            tmdb_client: An initialized TMDBClient instance
            omdb_client: An initialized OMDBClient instance
        """
        self.tmdb_adapter = TMDBDataAdapter(tmdb_client)
        self.omdb_adapter = OMDBDataAdapter(omdb_client)

    async def import_movie_with_enrichment(
        self,
        session: Session,
        tmdb_id: int,
        language: str = "en-US",
        include_credits: bool = True,
        include_videos: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Import a movie from TMDB and enrich it with OMDB data.

        Args:
            session: Database session
            tmdb_id: TMDB movie ID
            language: Language for movie data (default: "en-US")
            include_credits: Whether to include credits information (default: True)
            include_videos: Whether to include video/trailer information (default: True)

        Returns:
            Dictionary with import result information, or None if import failed
        """
        ***REMOVED*** First import the movie from TMDB
        result = await self.tmdb_adapter.import_movie_by_id(
            session, tmdb_id, language, include_credits, include_videos
        )

        if not result:
            return None

        ***REMOVED*** Get the movie details for OMDB enrichment
        db_movie_id = result.get("movie_id")
        if db_movie_id is None:
            logger.warning("Missing movie_id in import result")
            return result

        db_movie = get_movie_by_id(session, db_movie_id)
        if not db_movie or db_movie.id is None:
            return result

        ***REMOVED*** Extract year from release date if available
        year = None
        if db_movie.release_date:
            year = str(db_movie.release_date.year)

        ***REMOVED*** Enrich with OMDB data
        enriched = await self.omdb_adapter.enrich_movie(session, db_movie.id, db_movie.title, year)

        if enriched:
            result["omdb_enriched"] = True

        return result

    async def import_popular_movies_with_enrichment(
        self, session: Session, limit: int = 10, language: str = "en-US"
    ) -> List[Dict[str, Any]]:
        """Import popular movies from TMDB and enrich them with OMDB data.

        Args:
            session: Database session
            limit: Maximum number of movies to import (default: 10)
            language: Language for movie data (default: "en-US")

        Returns:
            List of import result dictionaries
        """
        results = []
        tmdb_results = await self.tmdb_adapter.import_popular_movies(session, limit, language)

        for result in tmdb_results:
            ***REMOVED*** Get the movie details for OMDB enrichment
            db_movie_id = result.get("movie_id")
            if db_movie_id is None:
                results.append(result)
                continue

            db_movie = get_movie_by_id(session, db_movie_id)
            if not db_movie or db_movie.id is None:
                results.append(result)
                continue

            ***REMOVED*** Extract year from release date if available
            year = None
            if db_movie.release_date:
                year = str(db_movie.release_date.year)

            ***REMOVED*** Enrich with OMDB data
            enriched = await self.omdb_adapter.enrich_movie(
                session, db_movie.id, db_movie.title, year
            )

            if enriched:
                result["omdb_enriched"] = True

            results.append(result)

        return results
