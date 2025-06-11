"""User interaction operations for backend API."""

import logging
from typing import Dict, List, Optional, Any, cast

from .base import BaseBackendClient, BackendClientError

logger = logging.getLogger(__name__)


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
            BackendClientError: If request fails
        """
        try:
            headers = self._get_auth_headers(user_id)
            return await self._make_request(
                "GET",
                self._build_api_path(f"/user/movies/{movie_id}/interaction"),
                headers=headers,
            )
        except BackendClientError as e:
            if "404" in str(e):
                ***REMOVED*** Return None if interaction not found
                return None
            ***REMOVED*** Re-raise other errors
            raise

    ***REMOVED*** ============================================================================
    ***REMOVED*** Watchlist Operations
    ***REMOVED*** ============================================================================

    async def get_user_watchlist(
        self,
        user_id: int,
        jwt_token: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's watchlist.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Response containing list of watchlist movies with interaction data
        """
        headers = self._get_auth_headers(user_id)
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            self._build_api_path("/user/movies/watchlist"),
            params=params,
            headers=headers,
        )

    async def set_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Add a movie to a user's watchlist.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "PUT",
            self._build_api_path(f"/user/movies/{movie_id}/watchlist"),
            headers=headers,
        )

    async def unset_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Remove movie from user's watchlist.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT authentication token (not used - kept for compatibility)

        Returns:
            Updated user interaction data
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/movies/{movie_id}/watchlist"),
            headers=headers,
        )

    async def toggle_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie in user's watchlist. (DEPRECATED)

        This method is deprecated. Use set_user_movie_watchlist or
        unset_user_movie_watchlist instead.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "POST",
            self._build_api_path(f"/user/movies/{movie_id}/watchlist"),
            headers=headers,
        )

    ***REMOVED*** ============================================================================
    ***REMOVED*** Watched Operations
    ***REMOVED*** ============================================================================

    async def get_user_watched_movies(
        self,
        user_id: int,
        jwt_token: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's watched movies.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Response containing list of watched movies with interaction data
        """
        headers = self._get_auth_headers(user_id)
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            self._build_api_path("/user/movies/watched"),
            params=params,
            headers=headers,
        )

    async def set_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Set a movie as watched by a user.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "PUT",
            self._build_api_path(f"/user/movies/{movie_id}/watched"),
            headers=headers,
        )

    async def unset_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Unset a movie as watched by a user.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/movies/{movie_id}/watched"),
            headers=headers,
        )

    async def toggle_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie as watched for user. (DEPRECATED)

        This method is deprecated. Use set_user_movie_watched or
        unset_user_movie_watched instead.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "POST",
            self._build_api_path(f"/user/movies/{movie_id}/watched"),
            headers=headers,
        )

    ***REMOVED*** ============================================================================
    ***REMOVED*** Liked Operations
    ***REMOVED*** ============================================================================

    async def get_user_liked_movies(
        self,
        user_id: int,
        jwt_token: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's liked movies.

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Response containing list of liked movies with interaction data
        """
        headers = self._get_auth_headers(user_id)
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            self._build_api_path("/user/movies/liked"),
            params=params,
            headers=headers,
        )

    async def set_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Set a movie as liked by a user.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "PUT",
            self._build_api_path(f"/user/movies/{movie_id}/liked"),
            headers=headers,
        )

    async def unset_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Unset a movie as liked by a user.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/movies/{movie_id}/liked"),
            headers=headers,
        )

    async def toggle_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie as liked for user. (DEPRECATED)

        This method is deprecated. Use set_user_movie_liked or
        unset_user_movie_liked instead.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication (not used - kept for compatibility)

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = self._get_auth_headers(user_id)
        return await self._make_request(
            "POST",
            self._build_api_path(f"/user/movies/{movie_id}/liked"),
            headers=headers,
        )

    ***REMOVED*** ============================================================================
    ***REMOVED*** User Details & Category Operations
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
        """Get user's movie details by category (watchlist, watched, liked).

        Args:
            user_id: User ID
            jwt_token: JWT authentication token (not used - kept for compatibility)
            category: Category of movies (watchlist, watched, liked)
            page: Page number for pagination
            limit: Maximum number of items per page
            **filters: Additional filter parameters (imdb_rating, year, sort_by, sort_desc, etc.)

        Returns:
            Response containing list of movie details with interaction data
        """
        headers = self._get_auth_headers(user_id)
        params = {"page": page, "limit": limit}

        ***REMOVED*** Add any additional filter parameters
        params.update(filters)

        return await self._make_request(
            "GET",
            self._build_api_path(f"/user/movies/{category}"),
            params=params,
            headers=headers,
        )
