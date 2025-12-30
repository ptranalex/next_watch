"""Movie-related operations for backend API."""

from typing import Any, cast

from config.logging import get_logger
from fast_core.errors import (
    ResourceNotFoundException,
    ValidationException,
    critical_service_handler,
    optional_service_handler,
)

from bff_api.services.clients.base import BaseBackendClient

logger = get_logger(__name__)


class MoviesClient(BaseBackendClient):
    """Client for movie-related operations."""

    @critical_service_handler("backend-api", logger)
    async def get_movie(self, movie_id: int, user_id: int | None = None) -> dict[str, Any]:
        """Get movie details with user-specific data.

        This is a CRITICAL operation - movie detail pages must work.

        Args:
            movie_id: Movie ID
            user_id: Optional user ID for personalized data

        Returns:
            Movie data with user interactions

        Raises:
            ValidationException: If movie_id is invalid
            ResourceNotFoundException: If movie not found (preserves semantic meaning)
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
            # Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id),
            )

    @critical_service_handler("backend-api", logger)
    async def get_movies(
        self,
        page: int = 1,
        limit: int = 20,
        genre_id: int | None = None,
        user_id: int | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """Get movies list with filters and user data.

        This is a CRITICAL operation - main movie listings must work.

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
        # Validate pagination parameters
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

    @critical_service_handler("backend-api", logger)
    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Search movies.

        This is a CRITICAL operation - search functionality must work.

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
        # Validate search parameters
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

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={
            "results": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
        },
    )
    async def get_trending_movies(
        self,
        page: int = 1,
        limit: int = 20,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Get trending movies.

        This is an OPTIONAL operation - trending movies are nice-to-have.
        Uses graceful degradation to return empty results if service unavailable.

        Args:
            page: Page number
            limit: Items per page
            user_id: Optional user ID for personalized data

        Returns:
            Trending movies list (empty if service unavailable)
        """
        # Validate pagination parameters
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        params = {"page": page, "limit": limit, "trending": True}

        if user_id:
            if user_id <= 0:
                raise ValidationException("User ID must be a positive integer")
            params["user_id"] = user_id

        return await self._make_request("GET", self._build_api_path("/movies"), params=params)

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={
            "results": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
        },
    )
    async def get_popular_movies(
        self,
        page: int = 1,
        limit: int = 20,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Get popular movies.

        This is an OPTIONAL operation - popular movies are nice-to-have.
        Uses graceful degradation to return empty results if service unavailable.

        Args:
            page: Page number
            limit: Items per page
            user_id: Optional user ID for personalized data

        Returns:
            Popular movies list (empty if service unavailable)
        """
        # Validate pagination parameters
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        params = {"page": page, "limit": limit, "sort": "popularity", "sort_desc": True}

        if user_id:
            if user_id <= 0:
                raise ValidationException("User ID must be a positive integer")
            params["user_id"] = user_id

        return await self._make_request("GET", self._build_api_path("/movies"), params=params)

    @optional_service_handler(service_name="backend-api", logger=logger, fallback_value=[])
    async def get_movie_cast(self, movie_id: int) -> list[dict[str, Any]]:
        """Get movie cast and crew information.

        This is an OPTIONAL operation - cast data is enhancement information.
        Uses graceful degradation to return empty list if service unavailable.

        Args:
            movie_id: Movie ID

        Returns:
            List of cast members with character and actor details (empty if service unavailable)

        Raises:
            ValidationException: If movie_id is invalid
        """
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")

        try:
            response = await self._make_request(
                "GET", self._build_api_path(f"/movies/{movie_id}/cast")
            )
            return cast(list[dict[str, Any]], response.get("cast", []))
        except ResourceNotFoundException:
            # Re-raise with more specific message but let the decorator handle graceful degradation
            raise ResourceNotFoundException(
                detail=f"Cast information for movie {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id),
            )

    @optional_service_handler(service_name="backend-api", logger=logger, fallback_value=[])
    async def get_movie_trailers(self, movie_id: int) -> list[dict[str, Any]]:
        """Get movie trailers.

        This is an OPTIONAL operation - trailers are enhancement information.
        Uses graceful degradation to return empty list if service unavailable.

        Args:
            movie_id: Movie ID

        Returns:
            List of movie trailers (empty if service unavailable)

        Raises:
            ValidationException: If movie_id is invalid
        """
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")

        try:
            response = await self._make_request(
                "GET", self._build_api_path(f"/movies/{movie_id}/trailers")
            )
            # Handle both dict responses with trailers key and wrapped list responses
            if "trailers" in response:
                return cast(list[dict[str, Any]], response["trailers"])
            return cast(list[dict[str, Any]], response.get("data", []))
        except ResourceNotFoundException:
            # Re-raise with more specific message but let the decorator handle graceful degradation
            raise ResourceNotFoundException(
                detail=f"Trailers for movie {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id),
            )

    @critical_service_handler("backend-api", logger)
    async def get_movies_bulk(
        self,
        movie_ids: list[int],
        user_id: int | None = None,
        page: int = 1,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get multiple movies by their IDs using bulk endpoint.

        This is a CRITICAL operation - bulk movie fetching is essential for performance.

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
        # Validate parameters
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

        # Convert movie IDs to comma-separated string
        movie_ids_str = ",".join(map(str, movie_ids))
        params = {
            "ids": movie_ids_str,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", self._build_api_path("/movies/bulk"), params=params)
