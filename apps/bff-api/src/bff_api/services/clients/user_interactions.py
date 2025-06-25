"""User interaction operations for backend API."""

import logging
from typing import Any, Dict, List, Optional, cast

from config.logging import get_logger

from fast_core.errors import (
    ResourceNotFoundException,
    ExternalServiceException,
    service_error_handler,
)
from bff_api.services.clients.base import BaseBackendClient

logger = get_logger(__name__)


class UserInteractionsClient(BaseBackendClient):
    """Client for user interaction operations."""

    async def get_user_movie_interaction(
        self, user_id: int, movie_id: int, jwt_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a user's interaction with a movie.

        Args:
            user_id: User ID (already authenticated by BFF)
            movie_id: Movie ID
            jwt_token: JWT token (not used - kept for compatibility)

        Returns:
            User interaction data if found, None otherwise

        Raises:
            ExternalServiceException: If request fails
        """
        try:
            headers = self._get_auth_headers(user_id)
            return await self._make_request(
                "GET",
                self._build_api_path(f"/user/interactions/movies/{movie_id}"),
                headers=headers,
            )
        except ResourceNotFoundException:
            ***REMOVED*** Return None if interaction not found
            return None

    async def get_user_movie_interactions_batch(
        self, user_id: int, movie_ids: List[int], jwt_token: Optional[str] = None
    ) -> Dict[int, Optional[Dict[str, Any]]]:
        """Get a user's interactions with multiple movies in a single request.

        This method optimizes API calls by fetching multiple user-movie interactions
        in a single backend request instead of N individual requests.

        Args:
            user_id: User ID (already authenticated by BFF)
            movie_ids: List of movie IDs to get interactions for
            jwt_token: JWT token (not used - kept for compatibility)

        Returns:
            Dictionary mapping movie_id to interaction data (or None if no interaction)

        Raises:
            ExternalServiceException: If request fails
        """
        if not movie_ids:
            return {}

        ***REMOVED*** Remove duplicates and limit to reasonable batch size
        unique_movie_ids = list(set(movie_ids))[:100]  ***REMOVED*** Limit to 100 movies per batch

        try:
            headers = self._get_auth_headers(user_id)
            payload = {"movie_ids": unique_movie_ids}

            response = await self._make_request(
                "POST",
                self._build_api_path("/user/interactions/movies/batch"),
                data=payload,
                headers=headers,
            )

            ***REMOVED*** Convert string keys back to integers and handle the response format
            interactions_dict = response.get("interactions", {})
            result: Dict[int, Optional[Dict[str, Any]]] = {}

            for movie_id in unique_movie_ids:
                interaction_data = interactions_dict.get(str(movie_id))
                result[movie_id] = interaction_data

            return result

        except Exception as e:
            logger.warning(
                "Failed to get batch interactions, falling back to individual requests",
                user_id=user_id,
                movie_count=len(unique_movie_ids),
                error=str(e),
                service="bff",
                component="user_interactions_client",
            )

            ***REMOVED*** Fallback to individual requests if batch fails
            result = {}
            for movie_id in unique_movie_ids:
                try:
                    interaction = await self.get_user_movie_interaction(
                        user_id, movie_id, jwt_token
                    )
                    result[movie_id] = interaction
                except Exception:
                    result[movie_id] = None

            return result

    ***REMOVED*** ============================================================================
    ***REMOVED*** Watchlist Operations (Updated to use new collection endpoints)
    ***REMOVED*** ============================================================================

    async def get_user_watchlist(
        self,
        user_id: int,
        jwt_token: str,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get user's watchlist using new collection endpoint.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            page: Page number for pagination (default: 1)
            limit: Maximum number of items per page (default: 20)

        Returns:
            Fast-core formatted response with results, pagination, and metadata
        """
        headers = self._get_auth_headers(user_id)
        params = {"page": page, "limit": limit}

        response = await self._make_request(
            "GET",
            self._build_api_path("/user/watchlist"),
            params=params,
            headers=headers,
        )

        ***REMOVED*** Return the fast-core response directly (contains results, pagination, metadata)
        return response

    async def set_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Add a movie to a user's watchlist using new collection endpoint.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        headers = self._get_auth_headers(user_id)
        payload = {"movie_id": movie_id}

        return await self._make_request(
            "POST",
            self._build_api_path("/user/watchlist"),
            data=payload,
            headers=headers,
        )

    async def unset_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Remove movie from user's watchlist using new collection endpoint.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT authentication token (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/watchlist/movies/{movie_id}"),
            headers=headers,
        )

    async def toggle_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie in user's watchlist. (DEPRECATED)

        This method is deprecated but maintained for backward compatibility.
        It will check current status and add/remove accordingly.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        ***REMOVED*** Check current interaction status
        interaction = await self.get_user_movie_interaction(user_id, movie_id, jwt_token)

        if interaction and interaction.get("in_watchlist", False):
            ***REMOVED*** Remove from watchlist
            return await self.unset_user_movie_watchlist(user_id, movie_id, jwt_token)
        else:
            ***REMOVED*** Add to watchlist
            return await self.set_user_movie_watchlist(user_id, movie_id, jwt_token)

    ***REMOVED*** ============================================================================
    ***REMOVED*** Watched Operations (Updated to use new collection endpoints)
    ***REMOVED*** ============================================================================

    async def get_user_watched_movies(
        self,
        user_id: int,
        jwt_token: str,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get user's watched movies using new collection endpoint.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            page: Page number for pagination (default: 1)
            limit: Maximum number of items per page (default: 20)

        Returns:
            Fast-core formatted response with results, pagination, and metadata
        """
        headers = self._get_auth_headers(user_id)
        params = {"page": page, "limit": limit}

        response = await self._make_request(
            "GET",
            self._build_api_path("/user/watched-movies"),
            params=params,
            headers=headers,
        )

        ***REMOVED*** Return the fast-core response directly
        return response

    async def set_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Set a movie as watched by a user using new collection endpoint.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        headers = self._get_auth_headers(user_id)
        payload = {"movie_id": movie_id}

        return await self._make_request(
            "POST",
            self._build_api_path("/user/watched-movies"),
            data=payload,
            headers=headers,
        )

    async def unset_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Unset a movie as watched by a user using new collection endpoint.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/watched-movies/{movie_id}"),
            headers=headers,
        )

    async def toggle_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie as watched for user. (DEPRECATED)

        This method is deprecated but maintained for backward compatibility.
        It will check current status and add/remove accordingly.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        ***REMOVED*** Check current interaction status
        interaction = await self.get_user_movie_interaction(user_id, movie_id, jwt_token)

        if interaction and interaction.get("watched", False):
            ***REMOVED*** Remove from watched
            return await self.unset_user_movie_watched(user_id, movie_id, jwt_token)
        else:
            ***REMOVED*** Mark as watched
            return await self.set_user_movie_watched(user_id, movie_id, jwt_token)

    ***REMOVED*** ============================================================================
    ***REMOVED*** Liked Operations (Updated to use new collection endpoints)
    ***REMOVED*** ============================================================================

    async def get_user_liked_movies(
        self,
        user_id: int,
        jwt_token: str,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get user's liked movies using new collection endpoint.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            page: Page number for pagination (default: 1)
            limit: Maximum number of items per page (default: 20)

        Returns:
            Fast-core formatted response with results, pagination, and metadata
        """
        headers = self._get_auth_headers(user_id)
        params = {"page": page, "limit": limit}

        response = await self._make_request(
            "GET",
            self._build_api_path("/user/liked-movies"),
            params=params,
            headers=headers,
        )

        ***REMOVED*** Return the fast-core response directly
        return response

    async def set_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Set a movie as liked by a user using new collection endpoint.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        headers = self._get_auth_headers(user_id)
        payload = {"movie_id": movie_id}

        return await self._make_request(
            "POST",
            self._build_api_path("/user/liked-movies"),
            data=payload,
            headers=headers,
        )

    async def unset_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Unset a movie as liked by a user using new collection endpoint.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/liked-movies/{movie_id}"),
            headers=headers,
        )

    async def toggle_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie as liked for user. (DEPRECATED)

        This method is deprecated but maintained for backward compatibility.
        It will check current status and add/remove accordingly.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data

        Raises:
            ExternalServiceException: If request fails
        """
        ***REMOVED*** Check current interaction status
        interaction = await self.get_user_movie_interaction(user_id, movie_id, jwt_token)

        if interaction and interaction.get("liked", False):
            ***REMOVED*** Remove like
            return await self.unset_user_movie_liked(user_id, movie_id, jwt_token)
        else:
            ***REMOVED*** Add like
            return await self.set_user_movie_liked(user_id, movie_id, jwt_token)

    ***REMOVED*** ============================================================================
    ***REMOVED*** User Details & Category Operations (Updated for fast-core compatibility)
    ***REMOVED*** ============================================================================

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
        return cast(List[Dict[str, Any]], response.get("data", []))

    async def get_user_movie_details_by_category(
        self,
        user_id: int,
        jwt_token: str,
        category: str,
        page: int = 1,
        limit: int = 20,
        **filters: Any,
    ) -> Dict[str, Any]:
        """Get user's movie details by category using new collection endpoints.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            category: Category of movies (watchlist, watched, liked)
            page: Page number for pagination
            limit: Maximum number of items per page
            **filters: Additional filter parameters (kept for compatibility but may not be supported)

        Returns:
            Fast-core formatted response with results, pagination, and metadata
        """
        headers = self._get_auth_headers(user_id)
        params = {"page": page, "limit": limit}

        ***REMOVED*** Map old category names to new endpoints
        endpoint_map = {
            "watchlist": "/user/watchlist",
            "watched": "/user/watched-movies",
            "liked": "/user/liked-movies",
        }

        endpoint = endpoint_map.get(category)
        if not endpoint:
            raise ValueError(
                f"Invalid category: {category}. Must be one of: watchlist, watched, liked"
            )

        ***REMOVED*** Note: Additional filters may not be supported by new collection endpoints
        ***REMOVED*** They were part of the old detailed movie category endpoint that we removed

        return await self._make_request(
            "GET",
            self._build_api_path(endpoint),
            params=params,
            headers=headers,
        )
