"""Popular movie recommendation endpoints."""

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
    track_popular_recommendation,
)
from recommendation_api.dependencies.common import (
    get_recommendation_service,
)
from recommendation_api.models.recommendation import (
    RecommendationsResponse,
)
from recommendation_api.services.recommendation import RecommendationService

logger = get_logger(__name__)
router = APIRouter()


***REMOVED*** Custom key builder for popular movies
def _build_popular_movies_key(
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
    recommendation_service: RecommendationService | None = None,
    **kwargs,
) -> str:
    """Build a custom cache key for popular movies."""
    return build_cache_key(
        "popular",
        [f"limit:{limit}", f"rating:{min_rating}", f"votes:{min_vote_count}"],
        prefix="reco:",
    )


@redis_cache(
    ttl=2700,  ***REMOVED*** 45 minutes TTL
    key_builder=_build_popular_movies_key,
    enable_metrics=True,
)
async def _get_popular_recommendations_data(
    limit: int,
    min_rating: float,
    min_vote_count: int,
    recommendation_service: RecommendationService,
) -> dict[str, Any]:
    """Internal cached function for popular recommendations data.

    This function returns a dictionary that can be JSON serialized for caching.
    Following the BFF pattern: cached functions return dicts, endpoints return Pydantic models.
    """
    recommendations, filters = await recommendation_service.get_popular_recommendations_direct(
        limit=limit,
        min_rating=min_rating,
        min_vote_count=min_vote_count,
    )

    ***REMOVED*** Convert MovieRecommendation objects to dictionaries for caching
    ***REMOVED*** Use mode="json" to ensure proper serialization of date objects
    recommendations_dicts = [rec.model_dump(mode="json") for rec in recommendations]

    ***REMOVED*** Return as dictionary for caching
    return {
        "recommendations": recommendations_dicts,
        "total": len(recommendations),
        "type": "popular",
        "filters": filters,
    }


@router.get("/popular", response_model=RecommendationsResponse)
@track_popular_recommendation
@optional_service_handler(
    service_name="recommendation-backend",
    logger=logger,
    fallback_value={
        "recommendations": [],
        "total": 0,
        "filters": {
            "min_rating": 7.0,
            "min_vote_count": 1000,
            "limit": 20,
            "graceful_degradation": True,
        },
        "metadata": {
            "service": "recommendation-api",
            "fallback_reason": "backend_service_unavailable",
        },
    },
    operation_name="get_popular_recommendations",
)
async def get_popular_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationsResponse:
    """Get popular movie recommendations.

    Uses graceful degradation - returns empty list if backend is unavailable.

    Args:
        limit: Maximum number of popular movies (1-100)
        min_rating: Minimum movie rating threshold (0-10)
        min_vote_count: Minimum vote count threshold
        recommendation_service: Recommendation service dependency

    Returns:
        Popular movie recommendations with graceful fallback

    Raises:
        ValidationException: If parameters are invalid
    """
    ***REMOVED*** Validate parameters
    if limit <= 0 or limit > 100:
        raise ValidationException("Limit must be between 1 and 100")
    if min_rating < 0 or min_rating > 10:
        raise ValidationException("Minimum rating must be between 0 and 10")
    if min_vote_count < 0:
        raise ValidationException("Minimum vote count must be non-negative")

    ***REMOVED*** Record recommendation request metrics
    metrics = get_recommendation_metrics()
    if metrics:
        ***REMOVED*** Record filter usage for popular movies
        metrics.record_recommendation_filter_usage("min_rating", _categorize_rating(min_rating))
        metrics.record_recommendation_filter_usage(
            "min_vote_count", _categorize_vote_count(min_vote_count)
        )
        metrics.record_recommendation_filter_usage("limit", _categorize_limit(limit))

    logger.debug(
        "Processing popular recommendations request",
        limit=limit,
        min_rating=min_rating,
        min_vote_count=min_vote_count,
        service="recommendation-api",
        component="popular_recommendations",
        endpoint="get_popular_recommendations",
    )

    ***REMOVED*** Use the cached function to get data as dictionary
    data = await _get_popular_recommendations_data(
        limit=limit,
        min_rating=min_rating,
        min_vote_count=min_vote_count,
        recommendation_service=recommendation_service,
    )

    ***REMOVED*** Record successful popular recommendations request
    if metrics:
        metrics.record_recommendation_request("popular", "success", 0.0, data.get("total", 0))
        metrics.record_backend_api_request("get_popular_movies", "success", 0.0)

    logger.debug(
        "Successfully processed popular recommendations request",
        total_recommendations=data.get("total", 0),
        service="recommendation-api",
        component="popular_recommendations",
        endpoint="get_popular_recommendations",
    )

    ***REMOVED*** Convert dictionary back to Pydantic model for response
    return RecommendationsResponse(**data)


def _categorize_rating(rating: float) -> str:
    """Categorize rating for metrics."""
    if rating < 6.0:
        return "low"
    elif rating < 8.0:
        return "medium"
    else:
        return "high"


def _categorize_vote_count(count: int) -> str:
    """Categorize vote count for metrics."""
    if count < 500:
        return "low"
    elif count < 2000:
        return "medium"
    else:
        return "high"


def _categorize_limit(limit: int) -> str:
    """Categorize limit for metrics."""
    if limit <= 20:
        return "small"
    elif limit <= 50:
        return "medium"
    else:
        return "large"
