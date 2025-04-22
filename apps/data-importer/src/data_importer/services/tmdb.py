import os
import logging
import aiohttp
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


class TMDBClient:
    """Client for The Movie Database API."""

    def __init__(
        self,
        access_token: str = "",
        base_url: str = "https://api.themoviedb.org/3",
    ):
        """Initialize the TMDB client.

        Args:
            access_token: Bearer token for TMDB API authentication
            base_url: Base URL for TMDB API requests
        """
        self.access_token = access_token
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

        if not self.access_token:
            logger.warning(
                "TMDB access token not provided. API calls will fail without authentication."
            )

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure an aiohttp session exists.

        Returns:
            An aiohttp ClientSession
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session  ***REMOVED*** type: ignore

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the TMDB API.

        Args:
            endpoint: The endpoint to request
            params: Optional parameters to include in the request

        Returns:
            A dictionary containing the response data
        """
        if params is None:
            params = {}

        url = f"{self.base_url}{endpoint}"
        session = await self._ensure_session()

        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        else:
            logger.error("No TMDB access token provided for API request")
            return {}

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(
                url, params=params, headers=headers, timeout=timeout
            ) as response:
                if response.status != 200:
                    logger.error(
                        f"Error fetching from TMDB: {response.status} {await response.text()}"
                    )
                    return {}
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"TMDB API request failed: {str(e)}")
            return {}

    async def get_popular_movies(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get popular movies from TMDB.

        Args:
            page: The page number to fetch (default: 1)

        Returns:
            A list of movie data dictionaries from TMDB
        """
        data = await self._make_request("/movie/popular", {"page": page})
        return data.get("results", [])

    async def get_movie_genres(self, language: str = "en-US") -> List[Dict[str, Any]]:
        """Get the list of official movie genres from TMDB.

        Args:
            language: Language for the genre names (default: en-US)

        Returns:
            A list of genre dictionaries with id and name
        """
        data = await self._make_request("/genre/movie/list", {"language": language})
        return data.get("genres", [])

    async def fetch_movies_by_year(self, year: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch movies released in a specific year from TMDB.

        Args:
            year: The primary release year to filter movies
            limit: Maximum number of movies to return (default: 10)

        Returns:
            A list of movie data dictionaries from TMDB

        Raises:
            aiohttp.ClientError: If there's a network error
            ValueError: If the API returns an error response
        """
        params: Dict[str, Any] = {
            "primary_release_year": year,
            "language": "en-US",
            "sort_by": "vote_count.desc",
            "include_adult": "false",
            "include_video": "false",
        }

        movies: List[Dict[str, Any]] = []
        page = 1

        try:
            while len(movies) < limit:
                params["page"] = page

                response = await self._make_request("/discover/movie", params)

                ***REMOVED*** If _make_request returns an empty dict, there was an error
                if not response:
                    raise ValueError(f"Error fetching movies for year {year}")

                ***REMOVED*** Check if we have results
                results = response.get("results", [])
                if not results:
                    break

                ***REMOVED*** Add only up to the limit
                remaining = limit - len(movies)
                movies.extend(results[:remaining])

                ***REMOVED*** Check if we've reached the last page
                if page >= response.get("total_pages", 1) or not remaining:
                    break

                page += 1

            return movies[:limit]  ***REMOVED*** Ensure we don't exceed the limit

        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching movies for year {year}: {str(e)}")
            raise

    async def get_movie_details(
        self, movie_id: int, language: str = "en-US", append_credits: bool = True
    ) -> Dict[str, Any]:
        """Get detailed information about a specific movie including credits if requested.

        Uses the TMDB movie details endpoint with optional append_to_response for credits.

        Args:
            movie_id: The TMDB ID of the movie
            language: Language for the movie data (default: en-US)
            append_credits: Whether to include credits data in the response (default: True)

        Returns:
            A dictionary containing the movie details and optionally credits

        Raises:
            ValueError: If the movie_id is invalid or the API returns an error
        """
        params: Dict[str, Any] = {"language": language}

        if append_credits:
            params["append_to_response"] = "credits"

        endpoint = f"/movie/{movie_id}"
        response = await self._make_request(endpoint, params)

        if not response:
            logger.error(f"Failed to fetch details for movie ID: {movie_id}")
            raise ValueError(f"Could not retrieve details for movie ID: {movie_id}")

        return response
