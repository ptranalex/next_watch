"""Backend API client for BFF service."""

import logging
from typing import Dict, List, Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from bff_api.config.app import Config

logger = logging.getLogger(__name__)


class BackendClientError(Exception):
    """Base exception for backend client errors."""

    pass


class BackendClient:
    """HTTP client for communicating with backend API."""

    def __init__(self, config: Config):
        """Initialize backend client.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.base_url = config.backend_api_url
        self.timeout = config.backend_api_timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _build_api_path(self, path: str) -> str:
        """Build API path with version prefix.

        Args:
            path: Relative API path

        Returns:
            Full API path with version prefix
        """
        ***REMOVED*** Remove leading slash if present to avoid double slashes
        clean_path = path.lstrip("/")
        return f"/api/v1/{clean_path}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "NextWatch-BFF/0.1.0",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            BackendClientError: If request fails
        """
        client = await self._get_client()

        try:
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=data,
                headers=headers or {},
            )
            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"data": response.text}

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} for {method} {path}: {e}"
            )
            raise BackendClientError(f"Backend API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {path}: {e}")
            raise BackendClientError(f"Backend API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {path}: {e}")
            raise BackendClientError(f"Unexpected backend error: {e}")

    async def get_movie(
        self, movie_id: int, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
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
        **filters,
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

        return await self._make_request(
            "GET", self._build_api_path("/movies"), params=params
        )

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

    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get all genres.

        Returns:
            List of genres
        """
        logger.info(f"Making request to {self._build_api_path('/genres')}")
        response = await self._make_request("GET", self._build_api_path("/genres"))
        logger.info(f"Raw genres response: {response}")
        ***REMOVED*** Handle both direct list responses and responses with a data field
        if isinstance(response, list):
            return response
        ***REMOVED*** Handle response with genres key
        if isinstance(response, dict) and "genres" in response:
            return response["genres"]
        return response.get("data", [])

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

    async def get_movie_cast(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get movie cast and crew information.

        Args:
            movie_id: Movie ID

        Returns:
            List of cast members with character and actor details
        """
        response = await self._make_request(
            "GET", self._build_api_path(f"/movies/{movie_id}/cast")
        )
        return response.get("cast", [])

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
        ***REMOVED*** Handle both list responses and dictionary responses with trailers key
        if isinstance(response, list):
            return response
        return response.get("trailers", [])

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
            reco_api_url = self.config.reco_api_url if hasattr(self.config, "reco_api_url") else "http://localhost:8002"
            
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
                return recommendations
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} getting similar movies for {movie_id}: {e}")
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

    async def get_actor(self, actor_id: int) -> Dict[str, Any]:
        """Get actor details.

        Args:
            actor_id: Actor ID

        Returns:
            Actor data
        """
        return await self._make_request(
            "GET", self._build_api_path(f"/actors/{actor_id}")
        )

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
            jwt_token: JWT authentication token
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Response containing list of watchlist movies with interaction data
        """
        headers = {"Authorization": f"Bearer {jwt_token}"}
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            self._build_api_path("/user/movies/watchlist"),
            params=params,
            headers=headers,
        )

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
            jwt_token: JWT authentication token
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Response containing list of liked movies with interaction data
        """
        headers = {"Authorization": f"Bearer {jwt_token}"}
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            self._build_api_path("/user/movies/liked"),
            params=params,
            headers=headers,
        )

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
        return response.get("data", [])

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
            ***REMOVED*** Use service-to-service authentication with internal API key
            ***REMOVED*** Pass user_id via X-User-ID header after service authentication
            headers = {
                "Authorization": f"Bearer {self.config.internal_api_key or 'bff-to-backend-secret-key'}",
                "X-User-ID": str(user_id),
            }

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

    async def toggle_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Toggle movie in user's watchlist. (DEPRECATED)

        This method is deprecated. Use set_user_movie_watchlist or
        unset_user_movie_watchlist instead.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
        return await self._make_request(
            "POST",
            self._build_api_path(f"/user/movies/{movie_id}/watchlist"),
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
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
        return await self._make_request(
            "POST",
            self._build_api_path(f"/user/movies/{movie_id}/watched"),
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
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
        return await self._make_request(
            "POST",
            self._build_api_path(f"/user/movies/{movie_id}/liked"),
            headers=headers,
        )

    ***REMOVED*** ============================================================================
    ***REMOVED*** New RESTful user interaction methods
    ***REMOVED*** ============================================================================

    async def set_user_movie_watched(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Set a movie as watched by a user.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
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
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/movies/{movie_id}/watched"),
            headers=headers,
        )

    async def set_user_movie_liked(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Set a movie as liked by a user.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
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
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/movies/{movie_id}/liked"),
            headers=headers,
        )

    async def set_user_movie_watchlist(
        self, user_id: int, movie_id: int, jwt_token: str
    ) -> Dict[str, Any]:
        """Add a movie to a user's watchlist.

        Args:
            user_id: User ID
            movie_id: Movie ID
            jwt_token: JWT token for authentication

        Returns:
            Updated user interaction data

        Raises:
            BackendClientError: If request fails
        """
        headers = {"Authorization": f"Bearer {jwt_token}", "X-User-ID": str(user_id)}
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
            jwt_token: JWT authentication token

        Returns:
            Updated user interaction data
        """
        headers = {"Authorization": f"Bearer {jwt_token}"}

        return await self._make_request(
            "DELETE",
            self._build_api_path(f"/user/movies/{movie_id}/watchlist"),
            headers=headers,
        )

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
            jwt_token: JWT authentication token
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Response containing list of watched movies with interaction data
        """
        headers = {"Authorization": f"Bearer {jwt_token}"}
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            self._build_api_path("/user/movies/watched"),
            params=params,
            headers=headers,
        )

    async def get_user_movie_details_by_category(
        self,
        user_id: int,
        jwt_token: str,
        category: str,
        page: int = 1,
        limit: int = 20,
        **filters,
    ) -> Dict[str, Any]:
        """Get user's movie details by category (watchlist, watched, liked).

        Args:
            user_id: User ID
            jwt_token: JWT authentication token
            category: Category of movies (watchlist, watched, liked)
            page: Page number for pagination
            limit: Maximum number of items per page
            **filters: Additional filter parameters (imdb_rating, year, sort_by, sort_desc, etc.)

        Returns:
            Response containing list of movie details with interaction data
        """
        headers = {"Authorization": f"Bearer {jwt_token}"}
        params = {"page": page, "limit": limit}
        
        ***REMOVED*** Add any additional filter parameters
        params.update(filters)

        return await self._make_request(
            "GET",
            self._build_api_path(f"/user/movies/{category}"),
            params=params,
            headers=headers,
        )

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

        return await self._make_request(
            "GET", self._build_api_path("/movies/bulk"), params=params
        )
