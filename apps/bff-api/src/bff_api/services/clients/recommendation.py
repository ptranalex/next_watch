"""Recommendation-related operations for recommendation API."""

import logging
from typing import Any, Dict, List, cast

import httpx

from config.logging import get_logger
from fast_core.errors import (
    ValidationException,
    ResourceNotFoundException,
    ServiceUnavailableException,
    ExternalServiceException,
    service_error_handler,
)

from .base import BaseBackendClient

logger = get_logger(__name__)


class RecommendationClient(BaseBackendClient):
    """Client for recommendation-related operations."""

    @service_error_handler("recommendation-api", logger, "get_similar_movies")
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
            ValidationException: If parameters are invalid
            ResourceNotFoundException: If movie not found (but returns empty list by design)
            ServiceUnavailableException: If recommendation service is unavailable
        """
        ***REMOVED*** Validate parameters
        if movie_id <= 0:
            raise ValidationException("Movie ID must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")
        if min_score < 0 or min_score > 1:
            raise ValidationException("Minimum score must be between 0 and 1")

        try:
            ***REMOVED*** Use inherited HTTP client methods from BaseBackendClient
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

            logger.info(f"Fetched {len(recommendations)} similar movies for movie {movie_id}")
            return cast(List[Dict[str, Any]], recommendations)

        except ResourceNotFoundException:
            ***REMOVED*** If movie is not found, return empty list instead of raising error
            ***REMOVED*** This is a design decision for better UX - missing movies shouldn't break recommendations
            logger.info(
                f"Movie {movie_id} not found in recommendation service, returning empty list"
            )
            return []
        except (ServiceUnavailableException, ExternalServiceException):
            ***REMOVED*** Re-raise service errors as-is
            raise
        except ValidationException:
            ***REMOVED*** Re-raise validation errors as-is
            raise
