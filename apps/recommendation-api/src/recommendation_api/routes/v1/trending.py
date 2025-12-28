"""Trending movie recommendation endpoints."""

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
    track_trending_recommendation,
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


***REMOVED*** Custom key builder for trending movies
def _build_trending_movies_key(
    limit: int = 20,
    days: int = 7,
    min_rating: float | None = None,
    recommendation_service: RecommendationService | None = None,
    **kwargs,
) -> str:
    """Build a custom cache key for trending movies."""
    parts: list[str | int | None] = [f"limit:{limit}", f"days:{days}"]
    if min_rating is not None:
        parts.append(f"rating:{min_rating}")

    return build_cache_key("trending", parts, prefix="reco:")


@redis_cache(
    ttl=1800,  ***REMOVED*** 30 minutes TTL
    key_builder=_build_trending_movies_key,
    enable_metrics=True,
)
async def _get_trending_recommendations_data(
    limit: int,
    days: int,
    min_rating: float | None,
    recommendation_service: RecommendationService,
) -> dict[str, Any]:
    """Internal cached function for trending recommendations data.

    This function returns a dictionary that can be JSON serialized for caching.
    Following the BFF pattern: cached functions return dicts, endpoints return Pydantic models.
    """
    ***REMOVED*** Temporarily use popular_recommendations_direct as trending implementation
    ***REMOVED*** since get_trending_recommendations_direct doesn't exist yet
    min_vote_count = 1000  ***REMOVED*** Default value from other methods
    recommendations, filters = await recommendation_service.get_popular_recommendations_direct(
        limit=limit,
        min_rating=min_rating or 7.0,  ***REMOVED*** Default to 7.0 if None
        min_vote_count=min_vote_count,
    )

    ***REMOVED*** Update filters to include days parameter
    filters["days"] = days
    filters["type"] = "trending"  ***REMOVED*** Add type to filters

    ***REMOVED*** Convert MovieRecommendation objects to dictionaries for caching
    ***REMOVED*** Use mode="json" to ensure proper serialization of date objects
    recommendations_dicts = [rec.model_dump(mode="json") for rec in recommendations]

    ***REMOVED*** Return as dictionary for caching
    return {
        "recommendations": recommendations_dicts,
        "total": len(recommendations),
        "type": "trending",
        "filters": filters,
    }


@router.get("/trending", response_model=RecommendationsResponse)
@track_trending_recommendation
@optional_service_handler(
    service_name="recommendation-backend",
    logger=logger,
    fallback_value={
        "recommendations": [],
        "total": 0,
        "filters": {
            "days": 7,
            "min_rating": None,
            "limit": 20,
            "graceful_degradation": True,
        },
        "metadata": {
            "service": "recommendation-api",
            "fallback_reason": "backend_service_unavailable",
        },
    },
    operation_name="get_trending_recommendations",
)
async def get_trending_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30),
    min_rating: float | None = Query(None, ge=0, le=10),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationsResponse:
    """Get trending movie recommendations.

    Uses graceful degradation - returns empty list if backend is unavailable.

    Args:
        limit: Maximum number of trending movies (1-100)
        days: Number of days to look back for trending (1-30)
        min_rating: Optional minimum rating filter (0-10)
        recommendation_service: Recommendation service dependency

    Returns:
        Trending movie recommendations with graceful fallback

    Raises:
        ValidationException: If parameters are invalid
    """
    ***REMOVED*** Validate parameters
    if limit <= 0 or limit > 100:
        raise ValidationException("Limit must be between 1 and 100")
    if days <= 0 or days > 30:
        raise ValidationException("Days must be between 1 and 30")
    if min_rating is not None and (min_rating < 0 or min_rating > 10):
        raise ValidationException("Minimum rating must be between 0 and 10")

    ***REMOVED*** Record recommendation request metrics
    metrics = get_recommendation_metrics()
    if metrics:
        ***REMOVED*** Record filter usage for trending movies
        metrics.record_recommendation_filter_usage("days", _categorize_days(days))
        if min_rating is not None:
            metrics.record_recommendation_filter_usage("min_rating", _categorize_rating(min_rating))
        metrics.record_recommendation_filter_usage("limit", _categorize_limit(limit))

    logger.debug(
        "Processing trending recommendations request",
        limit=limit,
        days=days,
        min_rating=min_rating,
        service="recommendation-api",
        component="trending_recommendations",
        endpoint="get_trending_recommendations",
    )

    ***REMOVED*** Use the cached function to get data as dictionary
    data = await _get_trending_recommendations_data(
        limit=limit,
        days=days,
        min_rating=min_rating,
        recommendation_service=recommendation_service,
    )

    ***REMOVED*** Record successful trending recommendations request
    if metrics:
        metrics.record_recommendation_request("trending", "success", 0.0, data.get("total", 0))
        metrics.record_backend_api_request("get_trending_movies", "success", 0.0)

    logger.debug(
        "Successfully processed trending recommendations request",
        total_recommendations=data.get("total", 0),
        service="recommendation-api",
        component="trending_recommendations",
        endpoint="get_trending_recommendations",
    )

    ***REMOVED*** Convert dictionary back to Pydantic model for response
    return RecommendationsResponse(**data)


def _categorize_days(days: int) -> str:
    """Categorize days for metrics."""
    if days <= 3:
        return "short"
    elif days <= 14:
        return "medium"
    else:
        return "long"


def _categorize_rating(rating: float) -> str:
    """Categorize rating for metrics."""
    if rating < 6.0:
        return "low"
    elif rating < 8.0:
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
