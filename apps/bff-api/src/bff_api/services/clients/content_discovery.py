"""Content discovery operations for backend API."""

from typing import Any, Dict, List, Optional, cast
from config.logging import get_logger

from fast_core.errors import (
    ExternalServiceException,
    ResourceNotFoundException,
    ValidationException,
    critical_service_handler,
    optional_service_handler,
)
from bff_api.services.clients.base import BaseBackendClient

logger = get_logger(__name__)


class ContentDiscoveryClient(BaseBackendClient):
    """Client for content discovery operations."""

    @critical_service_handler("backend-api", logger)
    async def get_genre(self, genre_id: int) -> Dict[str, Any]:
        """Get a specific genre by ID.

        This is a CRITICAL operation - individual genre details are essential for genre pages.

        Args:
            genre_id: Genre ID

        Returns:
            Genre data

        Raises:
            ValidationException: If genre_id is invalid
            ResourceNotFoundException: If genre not found
        """
        if genre_id <= 0:
            raise ValidationException("Genre ID must be a positive integer")

        logger.info(
            "Fetching genre details from backend",
            genre_id=genre_id,
            service="bff",
            component="content_discovery",
            endpoint="get_genre",
        )

        try:
            response = await self._make_request("GET", self._build_api_path(f"/genres/{genre_id}"))
            logger.info(
                "Successfully fetched genre details",
                genre_id=genre_id,
                genre_name=response.get("name", "unknown"),
                service="bff",
                component="content_discovery",
                endpoint="get_genre",
            )
            return response
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Genre with ID {genre_id} not found",
                resource_type="Genre",
                resource_id=str(genre_id),
            )

    @critical_service_handler("backend-api", logger)
    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get all genres.

        This is a CRITICAL operation - genres are essential for movie browsing and filtering.

        Returns:
            List of genres

        Raises:
            ExternalServiceException: If request fails
        """
        logger.info(
            "Fetching genres from backend",
            service="bff",
            component="content_discovery",
            endpoint="get_genres",
        )
        response = await self._make_request("GET", self._build_api_path("/genres"))

        ***REMOVED*** Handle response with genres key
        if "genres" in response:
            genres = cast(List[Dict[str, Any]], response["genres"])
        else:
            genres = cast(List[Dict[str, Any]], response.get("data", []))

        logger.info(
            "Successfully fetched genres",
            genre_count=len(genres),
            service="bff",
            component="content_discovery",
            endpoint="get_genres",
        )
        return genres

    @optional_service_handler(service_name="backend-api", logger=logger, fallback_value=[])
    async def get_trending_genres(self) -> List[Dict[str, Any]]:
        """Get trending genres.

        This is an OPTIONAL operation - trending genres are discovery enhancements.
        Uses graceful degradation to return empty list if service unavailable.

        Returns:
            List of trending genres (empty if service unavailable)
        """
        logger.info(
            "Fetching trending genres from backend",
            service="bff",
            component="content_discovery",
            endpoint="get_trending_genres",
        )
        response = await self._make_request(
            "GET", self._build_api_path("/genres"), params={"trending": True}
        )

        ***REMOVED*** Handle response with genres key
        if "genres" in response:
            genres = cast(List[Dict[str, Any]], response["genres"])
        else:
            genres = cast(List[Dict[str, Any]], response.get("data", []))

        logger.info(
            "Successfully fetched trending genres",
            genre_count=len(genres),
            service="bff",
            component="content_discovery",
            endpoint="get_trending_genres",
        )
        return genres

    @critical_service_handler("backend-api", logger)
    async def get_actor(self, actor_id: int) -> Dict[str, Any]:
        """Get actor details.

        This is a CRITICAL operation - actor detail pages must work.

        Args:
            actor_id: Actor ID

        Returns:
            Actor data

        Raises:
            ValidationException: If actor_id is invalid
            ResourceNotFoundException: If actor not found
        """
        if actor_id <= 0:
            raise ValidationException("Actor ID must be a positive integer")

        logger.info(
            "Fetching actor details from backend",
            actor_id=actor_id,
            service="bff",
            component="content_discovery",
            endpoint="get_actor",
        )

        try:
            response = await self._make_request("GET", self._build_api_path(f"/actors/{actor_id}"))
            logger.info(
                "Successfully fetched actor details",
                actor_id=actor_id,
                service="bff",
                component="content_discovery",
                endpoint="get_actor",
            )
            return response
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Actor with ID {actor_id} not found",
                resource_type="Actor",
                resource_id=str(actor_id),
            )

    @optional_service_handler(service_name="backend-api", logger=logger, fallback_value=[])
    async def get_popular_actors(self, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular actors.

        This is an OPTIONAL operation - popular actors are discovery enhancements.
        Uses graceful degradation to return empty list if service unavailable.

        Args:
            page: Page number
            limit: Items per page

        Returns:
            List of popular actors (empty if service unavailable)
        """
        ***REMOVED*** Validate pagination parameters
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        logger.info(
            "Fetching popular actors from backend",
            page=page,
            limit=limit,
            service="bff",
            component="content_discovery",
            endpoint="get_popular_actors",
        )

        response = await self._make_request(
            "GET",
            self._build_api_path("/actors"),
            params={"page": page, "limit": limit, "popular": True},
        )

        ***REMOVED*** Handle response with actors key
        if "actors" in response:
            actors = cast(List[Dict[str, Any]], response["actors"])
        else:
            actors = cast(List[Dict[str, Any]], response.get("data", []))

        logger.info(
            "Successfully fetched popular actors",
            actor_count=len(actors),
            page=page,
            service="bff",
            component="content_discovery",
            endpoint="get_popular_actors",
        )
        return actors

    @critical_service_handler("backend-api", logger)
    async def search_actors(self, query: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Search actors.

        This is a CRITICAL operation - search functionality must work.

        Args:
            query: Search query
            page: Page number
            limit: Items per page

        Returns:
            Search results

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

        logger.info(
            "Searching actors from backend",
            query=query,
            page=page,
            limit=limit,
            service="bff",
            component="content_discovery",
            endpoint="search_actors",
        )

        response = await self._make_request(
            "GET",
            self._build_api_path("/actors/search"),
            params={"q": query.strip(), "page": page, "limit": limit},
        )

        logger.info(
            "Successfully searched actors",
            query=query,
            total=response.get("total", 0),
            service="bff",
            component="content_discovery",
            endpoint="search_actors",
        )
        return response
