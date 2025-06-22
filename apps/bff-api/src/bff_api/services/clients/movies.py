"""Movie-related operations for backend API."""

import logging
from typing import Any, Dict, List, Optional, cast

import httpx

from config.logging import get_logger
from fast_core.errors import (
    ValidationException,
    ResourceNotFoundException,
    service_error_handler,
)

from .base import BaseBackendClient

logger = get_logger(__name__)


class MoviesClient(BaseBackendClient):
    """Client for movie-related operations."""

    @service_error_handler("backend-api", logger, "get_movie")
    async def get_movie(self, movie_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get movie details with user-specific data.

        Args:
            movie_id: Movie ID
            user_id: Optional user ID for personalized data

        Returns:
            Movie data with user interactions

        Raises:
            ValidationException: If movie_id is invalid
            ResourceNotFoundException: If movie not found
        """
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")

        params = {}
        if user_id:
            if user_id <= 0:
                raise ValidationException("User ID must be a positive integer")
            params["user_id"] = user_id

        try:
            return await self._make_request(
                "GET", self._build_api_path(f"/movies/{movie_id}"), params=params
            )
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id),
            )

    @service_error_handler("backend-api", logger, "get_movies")
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

        Raises:
            ValidationException: If pagination parameters are invalid
        """
        ***REMOVED*** Validate pagination parameters
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        params = {"page": page, "limit": limit, **filters}

        if genre_id:
            if genre_id <= 0:
                raise ValidationException("Genre ID must be a positive integer")
            params["genre_id"] = genre_id
        if user_id:
            if user_id <= 0:
                raise ValidationException("User ID must be a positive integer")
            params["user_id"] = user_id

        return await self._make_request("GET", self._build_api_path("/movies"), params=params)

    @service_error_handler("backend-api", logger, "search_movies")
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

        Raises:
            ValidationException: If search parameters are invalid
        """
        ***REMOVED*** Validate search parameters
        if not query or not query.strip():
            raise ValidationException("Search query cannot be empty")
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        params = {
            "q": query.strip(),
            "page": page,
            "limit": limit,
        }

        if user_id:
            if user_id <= 0:
                raise ValidationException("User ID must be a positive integer")
            params["user_id"] = user_id

        return await self._make_request(
            "GET", self._build_api_path("/movies/search"), params=params
        )

    @service_error_handler("backend-api", logger, "get_movie_cast")
    async def get_movie_cast(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get movie cast and crew information.

        Args:
            movie_id: Movie ID

        Returns:
            List of cast members with character and actor details

        Raises:
            ValidationException: If movie_id is invalid
            ResourceNotFoundException: If movie not found
        """
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")

        try:
            response = await self._make_request(
                "GET", self._build_api_path(f"/movies/{movie_id}/cast")
            )
            return cast(List[Dict[str, Any]], response.get("cast", []))
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Cast information for movie {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id),
            )

    @service_error_handler("backend-api", logger, "get_movie_trailers")
    async def get_movie_trailers(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get movie trailers.

        Args:
            movie_id: Movie ID

        Returns:
            List of movie trailers

        Raises:
            ValidationException: If movie_id is invalid
            ResourceNotFoundException: If movie not found
        """
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")

        try:
            response = await self._make_request(
                "GET", self._build_api_path(f"/movies/{movie_id}/trailers")
            )
            ***REMOVED*** Handle both dict responses with trailers key and wrapped list responses
            if "trailers" in response:
                return cast(List[Dict[str, Any]], response["trailers"])
            return cast(List[Dict[str, Any]], response.get("data", []))
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Trailers for movie {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id),
            )

    @service_error_handler("backend-api", logger, "get_movies_bulk")
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
            limit: Items per page

        Returns:
            Dictionary containing movies data with pagination

        Raises:
            ValidationException: If parameters are invalid
        """
        ***REMOVED*** Validate parameters
        if not movie_ids:
            raise ValidationException("Movie IDs list cannot be empty")
        if any(movie_id <= 0 for movie_id in movie_ids):
            raise ValidationException("All movie IDs must be positive integers")
        if len(movie_ids) > 100:
            raise ValidationException("Cannot fetch more than 100 movies at once")
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        ***REMOVED*** Convert movie IDs to comma-separated string
        movie_ids_str = ",".join(map(str, movie_ids))
        params = {
            "ids": movie_ids_str,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", self._build_api_path("/movies/bulk"), params=params)
