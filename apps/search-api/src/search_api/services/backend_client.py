"""Backend API client for Search API.

This module provides a client for communicating with the Backend API
to retrieve movie data, apply filters, and get search results.
"""

from typing import Any
from urllib.parse import urljoin

import httpx
from config.logging import get_logger

from search_api.config.app import SearchAPIConfig

logger = get_logger(__name__)


class BackendAPIException(Exception):
    """Exception raised when Backend API requests fail."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class BackendAPIClient:
    """Client for interacting with the Backend API service."""

    def __init__(self, config: SearchAPIConfig):
        self.config = config
        self.base_url = config.backend_api_url.rstrip("/")
        self.timeout = config.backend_api_timeout
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Search-API/1.0.0",
        }

        ***REMOVED*** Add internal API key if configured
        if config.internal_api_key:
            self.headers["Internal-API-Key"] = config.internal_api_key

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an API endpoint."""
        return urljoin(self.base_url, endpoint.lstrip("/"))

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Backend API."""
        url = self._build_url(endpoint)

        logger.debug(f"Making {method} request to {url}", params=params)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method, url=url, params=params, json=json_data, headers=self.headers
                )

                if response.status_code >= 400:
                    error_msg = f"Backend API request failed: {response.status_code}"
                    error_data: dict[str, Any] | None = None
                    try:
                        raw_error_data = response.json()
                        if isinstance(raw_error_data, dict):
                            error_data = raw_error_data
                            error_msg += f" - {error_data.get('detail', 'Unknown error')}"
                        else:
                            error_msg += " - Unknown error"
                    except Exception:
                        error_msg += f" - {response.text}"

                    logger.error(error_msg)
                    raise BackendAPIException(
                        error_msg,
                        status_code=response.status_code,
                        response_data=error_data,
                    )

                result: dict[str, Any] = response.json()
                logger.debug(f"Backend API response: {len(str(result))} characters")
                return result

        except httpx.TimeoutException as e:
            error_msg = f"Backend API request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise BackendAPIException(error_msg) from e
        except httpx.ConnectError as e:
            error_msg = f"Could not connect to Backend API at {self.base_url}"
            logger.error(error_msg)
            raise BackendAPIException(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error calling Backend API: {str(e)}"
            logger.error(error_msg)
            raise BackendAPIException(error_msg) from e

    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        genre_id: int | None = None,
        actor_id: int | None = None,
        sort_by: str = "title",
        sort_desc: bool = False,
        imdb_rating: float | None = None,
        rotten_tomatoes_rating: int | None = None,
        metacritic_rating: int | None = None,
        year: int | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> dict[str, Any]:
        """Search movies by title through Backend API.

        Args:
            query: Search query string
            page: Page number for pagination
            limit: Number of results per page
            genre_id: Optional genre filter
            actor_id: Optional actor filter (TMDB ID)
            sort_by: Field to sort by
            sort_desc: Sort in descending order
            imdb_rating: Minimum IMDb rating filter
            rotten_tomatoes_rating: Minimum RT rating filter
            metacritic_rating: Minimum Metacritic rating filter
            year: Release year filter
            start_year: Start year filter (inclusive)
            end_year: End year filter (inclusive)

        Returns:
            Movie search results from Backend API
        """
        params = {
            "q": query,
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_desc": sort_desc,
        }

        ***REMOVED*** Add optional filters
        if genre_id is not None:
            params["genre_id"] = genre_id
        if actor_id is not None:
            params["actor_id"] = actor_id
        if imdb_rating is not None:
            params["imdb_rating"] = imdb_rating
        if rotten_tomatoes_rating is not None:
            params["rotten_tomatoes_rating"] = rotten_tomatoes_rating
        if metacritic_rating is not None:
            params["metacritic_rating"] = metacritic_rating
        if year is not None:
            params["year"] = year
        if start_year is not None:
            params["start_year"] = start_year
        if end_year is not None:
            params["end_year"] = end_year

        return await self._make_request("GET", "/api/v1/movies/search", params=params)

    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get search suggestions from Backend API.

        Args:
            query: Search query string
            limit: Maximum number of suggestions

        Returns:
            Suggestions from Backend API
        """
        params = {
            "query": query,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v1/search/suggestions", params=params)

    async def get_text_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get text-based suggestions from Backend API.

        Args:
            query: Search query prefix
            limit: Maximum number of suggestions

        Returns:
            Text suggestions from Backend API
        """
        params = {
            "query": query,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v1/search/suggestions/text", params=params)

    async def search_all_entities(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search across all entity types through Backend API.

        Args:
            query: Search query string
            page: Page number for pagination
            limit: Number of results per page
            types: Optional list of entity types to include

        Returns:
            Multi-entity search results from Backend API
        """
        params = {
            "query": query,
            "page": page,
            "limit": limit,
        }

        if types:
            params["types"] = types

        return await self._make_request("GET", "/api/v1/search", params=params)

    async def list_actors(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get a list of actors from Backend API.

        Args:
            page: Page number for pagination
            limit: Number of actors per page

        Returns:
            Actors list from Backend API
        """
        params = {
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v1/actors", params=params)

    async def list_movies(
        self,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "imdb_rating",
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        """Get a list of movies from Backend API.

        Args:
            page: Page number for pagination
            limit: Number of movies per page
            sort_by: Field to sort by
            sort_desc: Sort in descending order

        Returns:
            Movies list from Backend API
        """
        params = {
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_desc": sort_desc,
        }

        return await self._make_request("GET", "/api/v1/movies", params=params)

    async def health_check(self) -> dict[str, Any]:
        """Check Backend API health.

        Returns:
            Health status from Backend API
        """
        return await self._make_request("GET", "/health")
