"""Similar movie recommendations endpoint for Recommendation API v1."""

from typing import Any

from cache.decorators import redis_cache
from cache.keys import build_cache_key
from config.logging import get_logger
from fast_core.errors import (
    ValidationException,
    optional_service_handler,
)
from fastapi import APIRouter, Depends, Query

from recommendation_api.core.metrics import (
    get_recommendation_metrics,
    track_similar_recommendation,
)
from recommendation_api.dependencies.common import (
    get_recommendation_service,
)
from recommendation_api.models.recommendation import (
    SimilarMoviesResponse,
)
from recommendation_api.services.recommendation import RecommendationService

logger = get_logger(__name__)
router = APIRouter()


# Custom key builder for similar movies
def _build_similar_movies_key(
    movie_id: int,
    limit: int = 20,
    min_score: float = 0.01,
    recommendation_service: RecommendationService | None = None,
    **kwargs,
) -> str:
    """Build a custom cache key for similar movies."""
    return build_cache_key(
        "similar", [movie_id, f"limit:{limit}", f"score:{min_score}"], prefix="reco:"
    )


@redis_cache(
    ttl=3600,  # 1 hour TTL
    key_builder=_build_similar_movies_key,
    enable_metrics=True,
)
async def _get_similar_movies_data(
    movie_id: int,
    limit: int,
    min_score: float,
    recommendation_service: RecommendationService,
) -> dict[str, Any]:
    """Internal cached function for similar movies data.

    This function returns a dictionary that can be JSON serialized for caching.
    Following the BFF pattern: cached functions return dicts, endpoints return Pydantic models.
    """
    if movie_id <= 0:
        raise ValueError("Invalid movie ID")

    logger.debug(f"Finding similar movies for movie ID {movie_id} with min_score={min_score}")

    recommendations, filters = await recommendation_service.get_similar_movies(
        movie_id=movie_id,
        limit=limit,
        min_score=min_score,
    )

    if "error" in filters:
        logger.debug(f"Error finding similar movies: {filters['error']}")
        raise ValueError(filters["error"])

    logger.debug(f"Found {len(recommendations)} similar movies for movie ID {movie_id}")

    # Convert MovieRecommendation objects to dictionaries for caching
    # Use mode="json" to ensure proper serialization of date objects
    recommendations_dicts = [rec.model_dump(mode="json") for rec in recommendations]

    # Return as dictionary for caching
    return {
        "recommendations": recommendations_dicts,
        "total": len(recommendations),
        "type": "similar",
        "movie_id": movie_id,
        "filters": filters,
    }


@router.get("/movies/{movie_id}/similar", response_model=SimilarMoviesResponse)
@track_similar_recommendation
async def get_similar_movies_endpoint(
    movie_id: int,
    limit: int = Query(20, ge=1, le=50),
    min_score: float = Query(0.01, ge=0, le=1.0),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> SimilarMoviesResponse:
    """Get movies similar to a specific movie.

    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of similar movies (1-50)
        min_score: Minimum similarity score threshold (0-1)
        recommendation_service: Recommendation service dependency

    Returns:
        Similar movie recommendations with graceful degradation if recommendation engine fails

    Raises:
        ValidationException: If movie_id is invalid
        ResourceNotFoundException: If movie is not found
    """
    # Validate movie_id
    if movie_id <= 0:
        raise ValidationException("Movie ID must be a positive integer")

    # Apply the error handler decorator with fallback logic
    @optional_service_handler(
        service_name="recommendation-engine",
        logger=logger,
        fallback_value={
            "recommendations": [],
            "total": 0,
            "type": "similar",
            "movie_id": movie_id,
            "filters": {
                "source_movie_id": movie_id,
                "min_score": min_score,
                "limit": limit,
                "graceful_degradation": True,
            },
            "metadata": {
                "service": "recommendation-api",
                "fallback_reason": "recommendation_service_unavailable",
            },
        },
        operation_name="get_similar_movies",
    )
    async def _get_similar_movies_with_error_handling():
        """Inner function to handle the actual similar movies logic."""

        # Record recommendation request metrics
        metrics = get_recommendation_metrics()
        if metrics:
            # Record filter usage for similar movies
            metrics.record_recommendation_filter_usage(
                "min_score", _categorize_similarity_score(min_score)
            )
            metrics.record_recommendation_filter_usage("limit", _categorize_limit(limit))

        # Routine start log at DEBUG
        logger.debug(
            f"Processing similar movies request - movie_id=={movie_id}, limit={limit}, min_score={min_score}",
            extra={
                "movie_id": movie_id,
                "limit": limit,
                "min_score": min_score,
                "service": "recommendation-api",
                "component": "similar_movies",
                "endpoint": "get_similar_movies",
            },
        )

        # Use the cached function to get data as dictionary
        data = await _get_similar_movies_data(
            movie_id=movie_id,
            limit=limit,
            min_score=min_score,
            recommendation_service=recommendation_service,
        )

        # Record successful similar movies request
        if metrics:
            metrics.record_recommendation_request("similar", "success", 0.0, data.get("total", 0))
            metrics.record_vector_operation("search_similar", "success", 0.0)

        # Routine success log at DEBUG
        logger.debug(
            f"Successfully processed similar movies request - movie_id={movie_id}, total_recommendations={data.get('total', 0)}",
            extra={
                "movie_id": movie_id,
                "total_recommendations": data.get("total", 0),
                "service": "recommendation-api",
                "component": "similar_movies",
                "endpoint": "get_similar_movies",
            },
        )

        return data

    # Execute the error-handled function
    data = await _get_similar_movies_with_error_handling()

    # Convert dictionary back to Pydantic model for response
    return SimilarMoviesResponse(**data)


def _categorize_similarity_score(score: float) -> str:
    """Categorize similarity score for metrics."""
    if score >= 0.8:
        return "high"
    elif score >= 0.5:
        return "medium"
    else:
        return "low"


def _categorize_limit(limit: int) -> str:
    """Categorize limit for metrics."""
    if limit <= 10:
        return "small"
    elif limit <= 20:
        return "medium"
    else:
        return "large"
