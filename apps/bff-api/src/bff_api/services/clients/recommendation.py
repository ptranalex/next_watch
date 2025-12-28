"""Recommendation-related operations for recommendation API."""

from typing import Any, cast

from config.logging import get_logger
from fast_core.errors import (
    ResourceNotFoundException,
    ValidationException,
    optional_service_handler,
)

from bff_api.services.clients.base import BackendClientPermanentError, BaseBackendClient

logger = get_logger(__name__)


class RecommendationClient(BaseBackendClient):
    """Client for recommendation-related operations."""

    async def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Override _make_request to handle 404s specifically for recommendations."""
        try:
            return await super()._make_request(method, path, params, data, headers)
        except BackendClientPermanentError as e:
            ***REMOVED*** Convert 404 errors to ResourceNotFoundException for better handling
            if "404" in str(e):
                ***REMOVED*** Extract movie ID from path if possible
                movie_id = "unknown"
                if "/movies/" in path:
                    try:
                        ***REMOVED*** Extract movie ID from path like "/reco/v1/movies/3577/similar"
                        movie_id = path.split("/movies/")[1].split("/")[0]
                    except (IndexError, ValueError):
                        pass

                raise ResourceNotFoundException(
                    detail="Movie not found in recommendation service",
                    resource_type="Movie",
                    resource_id=movie_id,
                )
            ***REMOVED*** Re-raise other permanent errors
            raise

    @optional_service_handler(
        service_name="recommendation-api",
        logger=logger,
        fallback_value=[],
        operation_name="get_similar_movies",
    )
    async def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 20,
        min_score: float = 0.01,
    ) -> list[dict[str, Any]]:
        """Get similar movies from recommendation API.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of similar movies
            min_score: Minimum similarity score threshold

        Returns:
            List of similar movies (empty list if service unavailable)

        Raises:
            ValidationException: If parameters are invalid

        Note:
            This method uses graceful degradation - if the recommendation service
            is unavailable or the movie is not found, it returns an empty list
            instead of failing. This improves user experience by not breaking
            the movie detail page when recommendations are unavailable.
        """
        ***REMOVED*** Validate parameters
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")
        if min_score < 0 or min_score > 1:
            raise ValidationException("Minimum score must be between 0 and 1")

        ***REMOVED*** Use inherited HTTP client methods from BaseBackendClient
        ***REMOVED*** The @optional_service_handler decorator will automatically handle errors
        ***REMOVED*** and return an empty list if the service is unavailable
        response_data = await self._make_request(
            "GET",
            f"/reco/v1/movies/{movie_id}/similar",
            params={
                "limit": limit,
                "min_score": min_score,
            },
        )

        ***REMOVED*** Extract just the recommendation movie objects from the response
        recommendations = response_data.get("recommendations", [])

        logger.debug(
            f"Fetched {len(recommendations)} similar movies for movie {movie_id}"
        )
        return cast(list[dict[str, Any]], recommendations)
