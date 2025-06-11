"""Content discovery operations for backend API."""

import logging
from typing import Dict, List, Optional, Any, cast

from .base import BaseBackendClient, BackendClientError

logger = logging.getLogger(__name__)


class ContentDiscoveryClient(BaseBackendClient):
    """Client for content discovery operations."""

    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get all genres.

        Returns:
            List of genres
        """
        logger.info(f"Making request to {self._build_api_path('/genres')}")
        response = await self._make_request("GET", self._build_api_path("/genres"))
        logger.info(f"Raw genres response: {response}")
        ***REMOVED*** Handle response with genres key
        if "genres" in response:
            return cast(List[Dict[str, Any]], response["genres"])
        return cast(List[Dict[str, Any]], response.get("data", []))

    async def get_genre(self, genre_id: int) -> Dict[str, Any]:
        """Get a specific genre by ID.

        Args:
            genre_id: Genre ID

        Returns:
            Genre data

        Raises:
            BackendClientError: If genre not found or request fails
        """
        logger.info(f"Making request to {self._build_api_path(f'/genres/{genre_id}')}")
        return await self._make_request("GET", self._build_api_path(f"/genres/{genre_id}"))

    async def get_actor(self, actor_id: int) -> Dict[str, Any]:
        """Get actor details.

        Args:
            actor_id: Actor ID

        Returns:
            Actor data
        """
        return await self._make_request("GET", self._build_api_path(f"/actors/{actor_id}"))
