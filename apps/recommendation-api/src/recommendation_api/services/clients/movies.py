"""Movie-related operations for backend API."""

from typing import Any

from config.logging import get_logger

from recommendation_api.services.clients.base import BackendClientError, BaseBackendClient

logger = get_logger(__name__)


class MoviesClient(BaseBackendClient):
    """Client for movie-related operations."""

    async def get_movie(self, movie_id: int) -> dict[str, Any]:
        """Get movie details by ID.

        Args:
            movie_id: Movie ID

        Returns:
            Movie data
        """
        return await self._make_request("GET", self._build_api_path(f"/movies/{movie_id}"))

    async def get_movies(
        self,
        page: int = 1,
        limit: int = 20,
        **filters: Any,
    ) -> dict[str, Any]:
        """Get movies list with filters.

        Args:
            page: Page number
            limit: Items per page
            **filters: Additional filters (genre_id, imdb_rating, etc.)

        Returns:
            Movies list with pagination
        """
        params = {"page": page, "limit": limit, **filters}

        return await self._make_request("GET", self._build_api_path("/movies"), params=params)

    async def get_top_movies(
        self,
        page: int = 1,
        limit: int = 20,
        year: int | None = None,
        genre_id: int | None = None,
    ) -> dict[str, Any]:
        """Get top-rated movies.

        Args:
            page: Page number
            limit: Items per page
            year: Filter by release year
            genre_id: Filter by genre

        Returns:
            Top-rated movies list
        """
        params = {"page": page, "limit": limit}
        if year:
            params["year"] = year
        if genre_id:
            params["genre_id"] = genre_id

        return await self._make_request("GET", self._build_api_path("/movies/top"), params=params)

    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        **filters: Any,
    ) -> dict[str, Any]:
        """Search movies by title.

        Args:
            query: Search query
            page: Page number
            limit: Items per page
            **filters: Additional filters

        Returns:
            Search results
        """
        params = {"q": query, "page": page, "limit": limit, **filters}

        return await self._make_request(
            "GET", self._build_api_path("/movies/search"), params=params
        )

    async def get_movies_bulk(
        self,
        movie_ids: list[int],
        page: int = 1,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get multiple movies by their IDs using the bulk endpoint.

        Args:
            movie_ids: List of movie IDs to fetch
            page: Page number for pagination
            limit: Maximum number of movies per page

        Returns:
            List of movie details

        Raises:
            BackendClientError: If request fails
        """
        if not movie_ids:
            return []

        # Convert movie IDs to comma-separated string
        ids_str = ",".join(str(movie_id) for movie_id in movie_ids)

        params = {
            "ids": ids_str,
            "page": page,
            "limit": limit,
        }

        try:
            # Use the bulk endpoint to get all movies in one request
            response = await self._make_request(
                "GET", self._build_api_path("/movies/bulk"), params=params
            )

            # Extract results from the paginated response
            movies = response.get("results", [])
            logger.debug(
                f"Bulk request returned {len(movies)} movies out of {len(movie_ids)} requested"
            )

            return movies

        except BackendClientError as e:
            logger.warning(f"Bulk movie request failed: {e}. Falling back to individual requests.")

            # Fall back to individual requests if bulk fails
            movies = []
            for movie_id in movie_ids:
                try:
                    movie = await self.get_movie(movie_id)
                    movies.append(movie)
                except BackendClientError as fallback_e:
                    # Log but continue with other movies - use debug for 404s since they're expected
                    if "404" in str(fallback_e):
                        logger.debug(f"Movie {movie_id} not found in backend API, skipping")
                    else:
                        logger.warning(f"Failed to fetch movie {movie_id}: {fallback_e}")
                    continue

            logger.info(
                f"Fallback: Retrieved {len(movies)} out of {len(movie_ids)} requested movies individually"
            )
            return movies

    async def get_movies_batch(self, movie_ids: list[int]) -> list[dict[str, Any]]:
        """Get multiple movies by their IDs.

        This is an alias for get_movies_bulk with default parameters.

        Args:
            movie_ids: List of movie IDs to fetch

        Returns:
            List of movie details
        """
        return await self.get_movies_bulk(movie_ids=movie_ids)

    async def get_popular_movies(
        self,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> list[dict[str, Any]]:
        """Get popular movies from the backend API.

        Args:
            limit: Maximum number of movies (max 50 for /movies/top endpoint)
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count (not used directly, kept for API compatibility)

        Returns:
            List of popular movies
        """
        # Ensure limit doesn't exceed backend API maximum
        safe_limit = min(limit, 50)

        try:
            # Use the top movies endpoint with filtering
            response = await self._make_request(
                "GET",
                self._build_api_path("/movies/top"),
                params={
                    "limit": safe_limit,
                    "page": 1,
                },
            )

            # Extract movies from the response
            movies = response.get("results", [])

            # Filter by rating (min_vote_count is not supported by the API)
            filtered_movies = [
                movie for movie in movies if movie.get("imdb_rating", 0) >= min_rating
            ]

            logger.info(f"Retrieved {len(filtered_movies)} popular movies after filtering")

            # Return the filtered movies (up to the limit)
            return filtered_movies[:safe_limit]

        except BackendClientError as e:
            logger.error(f"Failed to get popular movies: {e}")
            return []

    async def get_personalized_movies(
        self,
        user_id: int,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> list[dict[str, Any]]:
        """Get personalized movie recommendations for a user.

        Args:
            user_id: User ID
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count

        Returns:
            List of personalized movie recommendations
        """
        # For now, use the recommendations endpoint with user_id
        # In a real implementation, this would call a user-specific recommendations endpoint
        try:
            # First try a user-specific endpoint if it exists
            response = await self._make_request(
                "GET",
                self._build_api_path(f"/users/{user_id}/recommendations"),
                params={
                    "limit": limit,
                    "min_rating": min_rating,
                    "min_vote_count": min_vote_count,
                },
            )
            return response.get("results", [])
        except BackendClientError:
            # Fall back to popular movies if user-specific endpoint fails
            logger.info(
                f"No personalized recommendations for user {user_id}, falling back to popular movies"
            )
            return await self.get_popular_movies(
                limit=limit,
                min_rating=min_rating,
                min_vote_count=min_vote_count,
            )

    async def get_trending_movies(
        self,
        limit: int = 20,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """Get trending movies from the backend API.

        Args:
            limit: Maximum number of movies (max 50)
            days: Time window in days (not used directly, kept for API compatibility)

        Returns:
            List of trending movies
        """
        # Ensure limit doesn't exceed backend API maximum for /movies/top endpoint
        safe_limit = min(limit, 50)

        try:
            # Use the top movies endpoint since there's no dedicated trending endpoint
            response = await self._make_request(
                "GET",
                self._build_api_path("/movies/top"),
                params={
                    "limit": safe_limit,
                    "page": 1,
                },
            )

            movies = response.get("results", [])
            logger.info(f"Retrieved {len(movies)} trending movies using top endpoint")
            return movies

        except BackendClientError as e:
            logger.error(f"Failed to get trending movies: {e}")
            return []

    async def get_recent_movies(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get recently updated movies from the backend API.

        Args:
            limit: Maximum number of movies (max 100 for /movies endpoint)

        Returns:
            List of recently updated movies
        """
        # Ensure limit doesn't exceed backend API maximum for /movies endpoint
        safe_limit = min(limit, 100)

        try:
            # Use regular movies endpoint with sorting since there's no dedicated recent endpoint
            response = await self._make_request(
                "GET",
                self._build_api_path("/movies"),
                params={
                    "limit": safe_limit,
                    "page": 1,
                    "sort_by": "release_date",
                    "sort_desc": True,
                },
            )

            movies = response.get("results", [])
            logger.info(f"Retrieved {len(movies)} recent movies using sorted endpoint")
            return movies

        except BackendClientError as e:
            logger.error(f"Failed to get recent movies: {e}")
            return []
