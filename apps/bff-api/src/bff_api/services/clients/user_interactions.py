"""User interaction operations for backend API."""

from typing import Any, cast

from config.logging import get_logger
from fast_core.errors import (
    ResourceNotFoundException,
    critical_service_handler,
    optional_service_handler,
)

from bff_api.services.clients.base import BaseBackendClient

logger = get_logger(__name__)


class UserInteractionsClient(BaseBackendClient):
    """Client for user interaction operations."""

    @critical_service_handler("backend-api", logger)
    async def get_user_movie_interaction(
        self, user_id: int, movie_id: int, jwt_token: str | None = None
    ) -> dict[str, Any] | None:
        """Get a user's interaction with a movie.

        This is a CRITICAL operation - user interaction data is essential for personalization.

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

    @critical_service_handler("backend-api", logger)
    async def get_user_movie_interactions_batch(
        self, user_id: int, movie_ids: list[int], jwt_token: str | None = None
    ) -> dict[int, dict[str, Any] | None]:
        """Get a user's interactions with multiple movies in a single request.

        This is a CRITICAL operation - batch user interactions are essential for performance.

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
        unique_movie_ids = list(set(movie_ids))[:100]

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
            result: dict[int, dict[str, Any] | None] = {}

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
    ***REMOVED*** Watchlist Operations (CRITICAL - Core User Feature)
    ***REMOVED*** ============================================================================

    @critical_service_handler("backend-api", logger)
    async def get_user_watchlist(
        self,
        user_id: int,
        jwt_token: str,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get user's watchlist using new collection endpoint.

        This is a CRITICAL operation - watchlist is core user functionality.

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

    @critical_service_handler("backend-api", logger)
    async def set_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Add a movie to a user's watchlist using new collection endpoint.

        This is a CRITICAL operation - watchlist modifications must work.

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

    @critical_service_handler("backend-api", logger)
    async def unset_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Remove movie from user's watchlist using new collection endpoint.

        This is a CRITICAL operation - watchlist modifications must work.

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

    @critical_service_handler("backend-api", logger)
    async def toggle_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Toggle movie in user's watchlist. (DEPRECATED)

        This is a CRITICAL operation - watchlist modifications must work.

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
    ***REMOVED*** Watched Operations (OPTIONAL - Nice-to-have tracking)
    ***REMOVED*** ============================================================================

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
    async def get_user_watched_movies(
        self,
        user_id: int,
        jwt_token: str,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get user's watched movies using new collection endpoint.

        This is an OPTIONAL operation - watched history is nice-to-have.
        Uses graceful degradation to return empty results if service unavailable.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            page: Page number for pagination (default: 1)
            limit: Maximum number of items per page (default: 20)

        Returns:
            Fast-core formatted response with results, pagination, and metadata (empty if service unavailable)
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

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={"success": False, "message": "Service unavailable"},
    )
    async def set_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Set a movie as watched by a user using new collection endpoint.

        This is an OPTIONAL operation - watched tracking is nice-to-have.
        Uses graceful degradation if service unavailable.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data (fallback if service unavailable)
        """
        headers = self._get_auth_headers(user_id)
        payload = {"movie_id": movie_id}

        return await self._make_request(
            "POST",
            self._build_api_path("/user/watched-movies"),
            data=payload,
            headers=headers,
        )

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={"success": False, "message": "Service unavailable"},
    )
    async def unset_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Unset a movie as watched by a user using new collection endpoint.

        This is an OPTIONAL operation - watched tracking is nice-to-have.
        Uses graceful degradation if service unavailable.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data (fallback if service unavailable)
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/watched-movies/{movie_id}"),
            headers=headers,
        )

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={"success": False, "message": "Service unavailable"},
    )
    async def toggle_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Toggle movie as watched for user. (DEPRECATED)

        This is an OPTIONAL operation - watched tracking is nice-to-have.
        Uses graceful degradation if service unavailable.

        This method is deprecated but maintained for backward compatibility.
        It will check current status and add/remove accordingly.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data (fallback if service unavailable)
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
    ***REMOVED*** Liked Operations (OPTIONAL - Social features)
    ***REMOVED*** ============================================================================

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
    async def get_user_liked_movies(
        self,
        user_id: int,
        jwt_token: str,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get user's liked movies using new collection endpoint.

        This is an OPTIONAL operation - liked movies are social features.
        Uses graceful degradation to return empty results if service unavailable.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            page: Page number for pagination (default: 1)
            limit: Maximum number of items per page (default: 20)

        Returns:
            Fast-core formatted response with results, pagination, and metadata (empty if service unavailable)
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

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={"success": False, "message": "Service unavailable"},
    )
    async def set_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Set a movie as liked by a user using new collection endpoint.

        This is an OPTIONAL operation - liked movies are social features.
        Uses graceful degradation if service unavailable.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data (fallback if service unavailable)
        """
        headers = self._get_auth_headers(user_id)
        payload = {"movie_id": movie_id}

        return await self._make_request(
            "POST",
            self._build_api_path("/user/liked-movies"),
            data=payload,
            headers=headers,
        )

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={"success": False, "message": "Service unavailable"},
    )
    async def unset_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Unset a movie as liked by a user using new collection endpoint.

        This is an OPTIONAL operation - liked movies are social features.
        Uses graceful degradation if service unavailable.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data (fallback if service unavailable)
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/liked-movies/{movie_id}"),
            headers=headers,
        )

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value={"success": False, "message": "Service unavailable"},
    )
    async def toggle_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> dict[str, Any]:
        """Toggle movie as liked for user. (DEPRECATED)

        This is an OPTIONAL operation - liked movies are social features.
        Uses graceful degradation if service unavailable.

        This method is deprecated but maintained for backward compatibility.
        It will check current status and add/remove accordingly.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Fast-core ActionResponse with success status and operation data (fallback if service unavailable)
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
    ***REMOVED*** User Details & Category Operations (OPTIONAL - Profile features)
    ***REMOVED*** ============================================================================

    @optional_service_handler(service_name="backend-api", logger=logger, fallback_value=[])
    async def get_user_favorites(self, user_id: int) -> list[dict[str, Any]]:
        """Get user's favorite movies.

        This is an OPTIONAL operation - favorites are profile features.
        Uses graceful degradation to return empty list if service unavailable.

        Args:
            user_id: User ID

        Returns:
            User's favorite movies (empty if service unavailable)
        """
        response = await self._make_request(
            "GET", self._build_api_path(f"/users/{user_id}/favorites")
        )
        return cast(list[dict[str, Any]], response.get("data", []))

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
    async def get_user_movie_details_by_category(
        self,
        user_id: int,
        jwt_token: str,
        category: str,
        page: int = 1,
        limit: int = 20,
        **filters: Any,
    ) -> dict[str, Any]:
        """Get user's movie details by category using new collection endpoints.

        This is an OPTIONAL operation - category browsing is a profile feature.
        Uses graceful degradation to return empty results if service unavailable.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            category: Category of movies (watchlist, watched, liked)
            page: Page number for pagination
            limit: Maximum number of items per page
            **filters: Additional filter parameters (kept for compatibility but may not be supported)

        Returns:
            Fast-core formatted response with results, pagination, and metadata (empty if service unavailable)
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
