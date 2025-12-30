import logging
from typing import Any, Dict, List, Optional, cast

import aiohttp

logger = logging.getLogger(__name__)


class OMDBClient:
    """Client for the Open Movie Database API."""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "http://www.omdbapi.com",
    ):
        """Initialize the OMDB client.

        Args:
            api_key: API key for The Open Movie Database API
            base_url: Base URL for OMDB API requests
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

        if not self.api_key:
            logger.warning("OMDB API key not provided. API calls will fail without authentication.")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure an aiohttp session exists.

        Returns:
            An aiohttp ClientSession
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the OMDB API.

        Args:
            params: Parameters to include in the request

        Returns:
            A dictionary containing the response data
        """
        if not self.api_key:
            logger.error("No OMDB API key provided for API request")
            return {"Response": "False", "Error": "No API key provided"}

        # Add API key to params
        params["apikey"] = self.api_key

        session = await self._ensure_session()

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(self.base_url, params=params, timeout=timeout) as response:
                if response.status != 200:
                    logger.error(
                        f"Error fetching from OMDB: {response.status} {await response.text()}"
                    )
                    return {
                        "Response": "False",
                        "Error": f"HTTP Error: {response.status}",
                    }

                result = await response.json()
                if result.get("Response") == "False":
                    logger.warning(f"OMDB API returned error: {result.get('Error')}")

                return cast(Dict[str, Any], result)

        except aiohttp.ClientError as e:
            logger.error(f"OMDB API request failed: {str(e)}")
            return {"Response": "False", "Error": str(e)}

    async def get_movie_by_imdb_id(self, imdb_id: str) -> Dict[str, Any]:
        """Retrieve movie information by IMDb ID.

        Args:
            imdb_id: The IMDb ID of the movie (e.g. tt1285016)

        Returns:
            A dictionary containing the movie information
        """
        params = {"i": imdb_id, "plot": "full", "r": "json"}
        return await self._make_request(params)

    async def search_movie(self, title: str, year: Optional[str] = None) -> Dict[str, Any]:
        """Search for a movie by title and optional year.

        Args:
            title: The title of the movie
            year: Optional year of release

        Returns:
            A dictionary containing the first search result if found
        """
        params = {"t": title, "r": "json"}
        if year:
            params["y"] = year

        return await self._make_request(params)

    async def search_movies(
        self, query: str, page: int = 1, type_filter: str = "movie"
    ) -> List[Dict[str, Any]]:
        """Search for movies matching the query.

        Args:
            query: Search query text
            page: Page number (1-100)
            type_filter: Type of result to return (movie, series, episode)

        Returns:
            A list of search results
        """
        params = {"s": query, "page": str(page), "r": "json"}
        if type_filter:
            params["type"] = type_filter

        response = await self._make_request(params)

        if response.get("Response") == "True" and "Search" in response:
            return cast(List[Dict[str, Any]], response["Search"])
        return []

    async def get_movie_by_title_and_year(self, title: str, year: str) -> Dict[str, Any]:
        """Get movie details by title and year.

        Args:
            title: The title of the movie
            year: The year the movie was released

        Returns:
            A dictionary containing the movie details
        """
        params = {"t": title, "y": year, "plot": "full", "r": "json"}
        return await self._make_request(params)

    async def get_season_episodes(self, imdb_id: str, season: int) -> List[Dict[str, Any]]:
        """Get episodes for a specific season of a TV series.

        Args:
            imdb_id: The IMDb ID of the TV series
            season: The season number

        Returns:
            A list of episodes for the specified season
        """
        params = {"i": imdb_id, "Season": str(season), "r": "json"}
        response = await self._make_request(params)

        if response.get("Response") == "True" and "Episodes" in response:
            return cast(List[Dict[str, Any]], response["Episodes"])
        return []
