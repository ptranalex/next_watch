"""ML API client for the Recommendation API.

This module provides a client for interacting with the ML API service
to generate embeddings for movies and user preferences.
"""

from typing import Any, cast

import httpx
from config.logging import get_logger
from httpx import Response

from recommendation_api.config import settings

logger = get_logger(__name__)


class MLApiClient:
    """Client for interacting with the ML API service."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        """Initialize the ML API client.

        Args:
            base_url: Base URL of the ML API service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.ml_api_url
        self.timeout = timeout
        logger.info(f"Initialized ML API client with base URL: {self.base_url}")

    async def _make_request(
        self, method: str, endpoint: str, json_data: dict[str, Any] | None = None
    ) -> Response:
        """Make a request to the ML API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json_data: JSON data to send

        Returns:
            HTTP response

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug(f"Making {method} request to {url}")

            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url, json=json_data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response

    async def generate_movie_embedding(self, movie_features: dict[str, Any]) -> list[float]:
        """Generate an embedding for a movie.

        Args:
            movie_features: Dictionary of movie features

        Returns:
            Embedding vector as list of floats

        Raises:
            httpx.HTTPError: If the request fails
        """
        ***REMOVED*** Prepare request data
        request_data = {
            "movie_id": str(movie_features.get("movie_id", "")),
            "title": movie_features.get("title", ""),
            "overview": movie_features.get("overview", ""),
            "genres": movie_features.get("genres", []),
            "additional_metadata": {
                "director": movie_features.get("director", ""),
                "cast": movie_features.get("cast", []),
                "release_year": movie_features.get("release_year", ""),
                "imdb_rating": movie_features.get("imdb_rating", ""),
            },
        }

        ***REMOVED*** Make request
        logger.debug(f"Generating embedding for movie {request_data['movie_id']}")
        response = await self._make_request("POST", "/api/v1/embeddings/movie", request_data)

        ***REMOVED*** Process response
        response_data = response.json()
        return cast(list[float], response_data["embedding"])

    async def generate_user_preference_vector(
        self,
        user_id: str,
        liked_movies: list[dict[str, Any]],
        watched_genres: dict[str, float],
    ) -> list[float]:
        """Generate a user preference vector.

        Args:
            user_id: User ID
            liked_movies: List of movies liked by the user with ratings
            watched_genres: Genres watched by the user with preference weights

        Returns:
            User preference vector as list of floats

        Raises:
            httpx.HTTPError: If the request fails
        """
        ***REMOVED*** Prepare request data
        request_data = {
            "user_id": user_id,
            "liked_movies": liked_movies,
            "watched_genres": watched_genres,
        }

        ***REMOVED*** Make request
        logger.debug(f"Generating preference vector for user {user_id}")
        response = await self._make_request("POST", "/api/v1/embeddings/user", request_data)

        ***REMOVED*** Process response
        response_data = response.json()
        return cast(list[float], response_data["preference_vector"])

    async def get_model_info(self) -> dict[str, Any]:
        """Get information about the embedding model.

        Returns:
            Dictionary with model information

        Raises:
            httpx.HTTPError: If the request fails
        """
        ***REMOVED*** Make request
        response = await self._make_request("GET", "/api/v1/embeddings/info")

        ***REMOVED*** Process response
        return cast(dict[str, Any], response.json())


***REMOVED*** Singleton instance
_ml_api_client: MLApiClient | None = None


def get_ml_api_client() -> MLApiClient:
    """Get the global ML API client instance.

    Returns:
        MLApiClient instance
    """
    global _ml_api_client

    if _ml_api_client is None:
        _ml_api_client = MLApiClient()

    return _ml_api_client
