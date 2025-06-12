"""Content discovery operations for backend API."""

from typing import Dict, List, Optional, Any, cast

from .base import BaseBackendClient, BackendClientError
from bff_api.config.logging import get_logger

logger = get_logger("bff_api.services.clients.content_discovery")


class ContentDiscoveryClient(BaseBackendClient):
    """Client for content discovery operations."""

    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get all genres.

        Returns:
            List of genres
        """
        try:
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

        except BackendClientError as e:
            logger.error(
                "Failed to fetch genres from backend",
                error=str(e),
                service="bff",
                component="content_discovery",
                endpoint="get_genres",
            )
            raise

    async def get_genre(self, genre_id: int) -> Dict[str, Any]:
        """Get a specific genre by ID.

        Args:
            genre_id: Genre ID

        Returns:
            Genre data

        Raises:
            BackendClientError: If genre not found or request fails
        """
        try:
            logger.info(
                "Fetching genre details from backend",
                genre_id=genre_id,
                service="bff",
                component="content_discovery",
                endpoint="get_genre",
            )
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

        except BackendClientError as e:
            logger.error(
                "Failed to fetch genre details from backend",
                genre_id=genre_id,
                error=str(e),
                service="bff",
                component="content_discovery",
                endpoint="get_genre",
            )
            raise

    async def get_actor(self, actor_id: int) -> Dict[str, Any]:
        """Get actor details.

        Args:
            actor_id: Actor ID

        Returns:
            Actor data

        Raises:
            BackendClientError: If actor not found or request fails
        """
        try:
            logger.info(
                "Fetching actor details from backend",
                actor_id=actor_id,
                service="bff",
                component="content_discovery",
                endpoint="get_actor",
            )
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

        except BackendClientError as e:
            logger.error(
                "Failed to fetch actor details from backend",
                actor_id=actor_id,
                error=str(e),
                service="bff",
                component="content_discovery",
                endpoint="get_actor",
            )
            raise
