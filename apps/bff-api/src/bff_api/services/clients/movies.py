"""Movie-related operations for backend API."""

import logging
from typing import Dict, List, Optional, Any, cast
import httpx

from .base import BaseBackendClient, BackendClientError

from bff_api.config.logging import get_logger

logger = get_logger("bff_api.services.clients.movies")


class MoviesClient(BaseBackendClient):
    """Client for movie-related operations."""

    async def get_movie(self, movie_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
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
        **filters: Any,
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

        return await self._make_request("GET", self._build_api_path("/movies"), params=params)

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

    async def get_movie_cast(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get movie cast and crew information.

        Args:
            movie_id: Movie ID

        Returns:
            List of cast members with character and actor details
        """
        response = await self._make_request("GET", self._build_api_path(f"/movies/{movie_id}/cast"))
        return cast(List[Dict[str, Any]], response.get("cast", []))

    async def get_movie_trailers(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get movie trailers.

        Args:
            movie_id: Movie ID

        Returns:
            List of movie trailers
        """
        response = await self._make_request(
            "GET", self._build_api_path(f"/movies/{movie_id}/trailers")
        )
        ***REMOVED*** Handle both dict responses with trailers key and wrapped list responses
        if "trailers" in response:
            return cast(List[Dict[str, Any]], response["trailers"])
        return cast(List[Dict[str, Any]], response.get("data", []))

    async def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 20,
        min_score: float = 0.01,
    ) -> List[Dict[str, Any]]:
        """Get similar movies from recommendation API.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of similar movies
            min_score: Minimum similarity score threshold

        Returns:
            List of similar movies

        Raises:
            BackendClientError: If request fails
        """
        try:
            ***REMOVED*** Get URL for recommendation API from config or construct it
            reco_api_url = (
                self.config.reco_api_url
                if hasattr(self.config, "reco_api_url")
                else "http://localhost:8002"
            )

            ***REMOVED*** Create a temporary client for recommendation API
            async with httpx.AsyncClient(base_url=reco_api_url, timeout=self.timeout) as client:
                response = await client.get(
                    f"/reco/v1/movies/{movie_id}/similar",
                    params={
                        "limit": limit,
                        "min_score": min_score,
                    },
                )
                response.raise_for_status()
                data = response.json()

                ***REMOVED*** Extract just the recommendation movie objects from the response
                recommendations = data.get("recommendations", [])

                logger.info(f"Fetched {len(recommendations)} similar movies for movie {movie_id}")
                return cast(List[Dict[str, Any]], recommendations)

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} getting similar movies for {movie_id}: {e}"
            )
            ***REMOVED*** If movie is not found, return empty list instead of raising error
            if e.response.status_code == 404:
                return []
            raise BackendClientError(f"Recommendation API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error getting similar movies for {movie_id}: {e}")
            raise BackendClientError(f"Recommendation API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting similar movies for {movie_id}: {e}")
            raise BackendClientError(f"Unexpected error getting similar movies: {e}")

    async def get_movies_bulk(
        self,
        movie_ids: List[int],
        user_id: Optional[int] = None,
        page: int = 1,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get multiple movies by their IDs using bulk endpoint.

        Args:
            movie_ids: List of movie IDs to fetch
            user_id: Optional user ID (not used by bulk endpoint, kept for compatibility)
            page: Page number for pagination
            limit: Maximum number of movies per page

        Returns:
            Response containing list of movie details

        Raises:
            BackendClientError: If request fails
        """
        if not movie_ids:
            return {"total": 0, "page": page, "per_page": limit, "results": []}

        ***REMOVED*** Convert movie IDs to comma-separated string
        ids_str = ",".join(str(movie_id) for movie_id in movie_ids)

        params = {
            "ids": ids_str,
            "page": page,
            "limit": limit,
        }

        ***REMOVED*** Note: user_id is not supported by the bulk endpoint
        ***REMOVED*** The bulk endpoint only returns basic movie data without user interactions

        return await self._make_request("GET", self._build_api_path("/movies/bulk"), params=params)
