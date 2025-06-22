"""Content discovery operations for backend API."""

from typing import Any, Dict, List, Optional, cast
from config.logging import get_logger

from fast_core.errors import (
    ExternalServiceException,
    ResourceNotFoundException,
    ValidationException,
    service_error_handler,
)
from bff_api.services.clients.base import BaseBackendClient

logger = get_logger(__name__)


class ContentDiscoveryClient(BaseBackendClient):
    """Client for content discovery operations."""

    @service_error_handler("backend-api", logger, "get_genres")
    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get all genres.

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

    @service_error_handler("backend-api", logger, "get_genre")
    async def get_genre(self, genre_id: int) -> Dict[str, Any]:
        """Get a specific genre by ID.

        Args:
            genre_id: Genre ID

        Returns:
            Genre data

        Raises:
            ValidationException: If genre_id is invalid
            ResourceNotFoundException: If genre not found
            ExternalServiceException: If request fails
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
            genre = await self._make_request("GET", self._build_api_path(f"/genres/{genre_id}"))

            logger.info(
                "Successfully fetched genre details",
                genre_id=genre_id,
                genre_name=genre.get("name"),
                service="bff",
                component="content_discovery",
                endpoint="get_genre",
            )
            return genre
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Genre with ID {genre_id} not found",
                resource_type="Genre",
                resource_id=str(genre_id),
            )

    @service_error_handler("backend-api", logger, "get_actor")
    async def get_actor(self, actor_id: int) -> Dict[str, Any]:
        """Get actor details.

        Args:
            actor_id: Actor ID

        Returns:
            Actor data

        Raises:
            ValidationException: If actor_id is invalid
            ResourceNotFoundException: If actor not found
            ExternalServiceException: If request fails
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
            actor = await self._make_request("GET", self._build_api_path(f"/actors/{actor_id}"))

            logger.info(
                "Successfully fetched actor details",
                actor_id=actor_id,
                actor_name=actor.get("name"),
                service="bff",
                component="content_discovery",
                endpoint="get_actor",
            )
            return actor
        except ResourceNotFoundException:
            ***REMOVED*** Re-raise with more specific message
            raise ResourceNotFoundException(
                detail=f"Actor with ID {actor_id} not found",
                resource_type="Actor",
                resource_id=str(actor_id),
            )
