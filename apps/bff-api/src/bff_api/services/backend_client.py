"""Backend API client for BFF service."""

import logging
from typing import Dict, List, Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from bff_api.config.app import Config

logger = logging.getLogger(__name__)


class BackendClientError(Exception):
    """Base exception for backend client errors."""

    pass


class BackendClient:
    """HTTP client for communicating with backend API."""

    def __init__(self, config: Config):
        """Initialize backend client.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.base_url = config.backend_api_url
        self.timeout = config.backend_api_timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _build_api_path(self, path: str) -> str:
        """Build API path with version prefix.

        Args:
            path: Relative API path

        Returns:
            Full API path with version prefix
        """
        ***REMOVED*** Remove leading slash if present to avoid double slashes
        clean_path = path.lstrip("/")
        return f"/api/v1/{clean_path}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "NextWatch-BFF/0.1.0",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            BackendClientError: If request fails
        """
        client = await self._get_client()

        try:
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=data,
                headers=headers or {},
            )
            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"data": response.text}

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} for {method} {path}: {e}"
            )
            raise BackendClientError(f"Backend API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {path}: {e}")
            raise BackendClientError(f"Backend API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {path}: {e}")
            raise BackendClientError(f"Unexpected backend error: {e}")

    async def get_movie(
        self, movie_id: int, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get movie details with user-specific data.

        Args:
            movie_id: Movie ID
            user_id: Optional user ID for personalized data

        Returns:
            Movie data with user interactions
        """
        params = {}
        if user_id:
            params["user_id"] = user_id

        return await self._make_request(
            "GET", self._build_api_path(f"/movies/{movie_id}"), params=params
        )

    async def get_movies(
        self,
        page: int = 1,
        limit: int = 20,
        genre_id: Optional[int] = None,
        user_id: Optional[int] = None,
        **filters,
    ) -> Dict[str, Any]:
        """Get movies list with filters and user data.

        Args:
            page: Page number
            limit: Items per page
            genre_id: Filter by genre
            user_id: Optional user ID for personalized data
            **filters: Additional filters

        Returns:
            Movies list with pagination and user interactions
        """
        params = {"page": page, "limit": limit, **filters}

        if genre_id:
            params["genre_id"] = genre_id
        if user_id:
            params["user_id"] = user_id

        return await self._make_request(
            "GET", self._build_api_path("/movies"), params=params
        )

    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search movies.

        Args:
            query: Search query
            page: Page number
            limit: Items per page
            user_id: Optional user ID for personalized data

        Returns:
            Search results with user interactions
        """
        params = {
            "q": query,
            "page": page,
            "limit": limit,
        }

        if user_id:
            params["user_id"] = user_id

        return await self._make_request(
            "GET", self._build_api_path("/movies/search"), params=params
        )

    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get all genres.

        Returns:
            List of genres
        """
        response = await self._make_request("GET", self._build_api_path("/genres"))
        return response.get("data", [])

    async def get_actor(self, actor_id: int) -> Dict[str, Any]:
        """Get actor details.

        Args:
            actor_id: Actor ID

        Returns:
            Actor data
        """
        return await self._make_request(
            "GET", self._build_api_path(f"/actors/{actor_id}")
        )

    async def get_user_watchlist(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's watchlist.

        Args:
            user_id: User ID

        Returns:
            User's watchlist
        """
        response = await self._make_request(
            "GET", self._build_api_path(f"/users/{user_id}/watchlist")
        )
        return response.get("data", [])

    async def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's favorite movies.

        Args:
            user_id: User ID

        Returns:
            User's favorite movies
        """
        response = await self._make_request(
            "GET", self._build_api_path(f"/users/{user_id}/favorites")
        )
        return response.get("data", [])
