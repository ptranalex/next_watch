"""Personalized movie recommendations endpoints."""

from config.logging import get_logger
from typing import Dict, Any, Optional

from cache.decorators import redis_cache
from cache.keys import build_cache_key
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import SQLAlchemyError

from fast_core.errors import (
    critical_service_handler,
    ValidationException,
    ResourceNotFoundException,
)

from recommendation_api.services.movie_adapter import MovieDataAdapter
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.dependencies.common import (
    get_movie_adapter_dependency,
    get_recommendation_service,
)
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    PersonalizedRecommendationsResponse,
)
from recommendation_api.core.metrics import (
    get_recommendation_metrics,
    track_personalized_recommendation,
)

logger = get_logger(__name__)

router = APIRouter()


***REMOVED*** Custom key builder for personalized movies
def _build_personalized_movies_key(
    user_id: int,
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
    recommendation_service: RecommendationService = None,
    **kwargs,
) -> str:
    """Build a custom cache key for personalized movies."""
    return build_cache_key(
        "personalized",
        [user_id, f"limit:{limit}", f"rating:{min_rating}", f"votes:{min_vote_count}"],
        prefix="reco:",
    )


@redis_cache(
    ttl=3600,  ***REMOVED*** 1 hour TTL
    key_builder=_build_personalized_movies_key,
    enable_metrics=True,
)
async def _get_personalized_recommendations_data(
    user_id: int,
    limit: int,
    min_rating: float,
    min_vote_count: int,
    recommendation_service: RecommendationService,
) -> Dict[str, Any]:
    """Internal cached function for personalized recommendations data.

    This function returns a dictionary that can be JSON serialized for caching.
    Following the BFF pattern: cached functions return dicts, endpoints return Pydantic models.
    """
    if user_id <= 0:
        raise ValueError("Invalid user ID")

    recommendations, filters = await recommendation_service.get_user_recommendations_direct(
        user_id=user_id,
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
        "type": "personalized",
        "user_id": user_id,
        "filters": filters,
    }


@router.get("/users/{user_id}/recommendations", response_model=PersonalizedRecommendationsResponse)
@track_personalized_recommendation
@critical_service_handler(
    service_name="recommendation-database",
    logger=logger,
    operation_name="get_personalized_recommendations",
)
async def get_personalized_recommendations_endpoint(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> PersonalizedRecommendationsResponse:
    """Get personalized movie recommendations for a user.

    This is a CRITICAL operation - personalized recommendations are core user functionality.

    Args:
        user_id: User ID to get recommendations for
        limit: Maximum number of recommendations (1-100)
        min_rating: Minimum movie rating threshold (0-10)
        min_vote_count: Minimum vote count threshold
        recommendation_service: Recommendation service dependency

    Returns:
        Personalized movie recommendations

    Raises:
        ValidationException: If user_id is invalid
        ResourceNotFoundException: If user is not found
    """
    ***REMOVED*** Validate user_id
    if user_id <= 0:
        raise ValidationException("User ID must be a positive integer")

    ***REMOVED*** Record recommendation request metrics
    metrics = get_recommendation_metrics()
    if metrics:
        ***REMOVED*** Record filter usage for personalized recommendations
        metrics.record_recommendation_filter_usage("min_rating", _categorize_rating(min_rating))
        metrics.record_recommendation_filter_usage(
            "min_vote_count", _categorize_vote_count(min_vote_count)
        )
        metrics.record_recommendation_filter_usage("limit", _categorize_limit(limit))

    logger.info(
        "Processing personalized recommendations request",
        user_id=user_id,
        limit=limit,
        min_rating=min_rating,
        min_vote_count=min_vote_count,
        service="recommendation-api",
        component="personalized_recommendations",
        endpoint="get_personalized_recommendations",
    )

    ***REMOVED*** Use the cached function to get data as dictionary
    data = await _get_personalized_recommendations_data(
        user_id=user_id,
        limit=limit,
        min_rating=min_rating,
        min_vote_count=min_vote_count,
        recommendation_service=recommendation_service,
    )

    ***REMOVED*** Record successful recommendation request
    if metrics:
        metrics.record_recommendation_request("personalized", "success", 0.0, data.get("total", 0))
        metrics.record_backend_api_request("get_personalized_movies", "success", 0.0)

    logger.info(
        "Successfully processed personalized recommendations request",
        user_id=user_id,
        total_recommendations=data.get("total", 0),
        service="recommendation-api",
        component="personalized_recommendations",
        endpoint="get_personalized_recommendations",
    )

    ***REMOVED*** Convert dictionary back to Pydantic model for response
    return PersonalizedRecommendationsResponse(**data)


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
    if limit <= 10:
        return "small"
    elif limit <= 50:
        return "medium"
    else:
        return "large"
