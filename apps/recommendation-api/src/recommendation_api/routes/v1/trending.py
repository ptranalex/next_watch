"""Trending movie recommendations endpoints."""

import logging
from typing import Dict, Any, Optional
from cache.decorators import redis_cache
from cache.keys import build_cache_key
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.services.movie_adapter import MovieDataAdapter
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.dependencies.common import (
    get_movie_adapter_dependency,
    get_recommendation_service,
)
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    RecommendationsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


***REMOVED*** Custom key builder for trending movies
def _build_trending_movies_key(
    limit: int = 20,
    days: int = 7,
    min_rating: Optional[float] = None,
    recommendation_service: RecommendationService = None,
    **kwargs,
) -> str:
    """Build a custom cache key for trending movies."""
    parts = [f"limit:{limit}", f"days:{days}"]
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
    min_rating: Optional[float],
    recommendation_service: RecommendationService,
) -> Dict[str, Any]:
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
async def get_trending_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationsResponse:
    """Get trending movie recommendations.

    Args:
        limit: Maximum number of recommendations (1-100)
        days: Number of days to look back for trending calculation (1-30)
        min_rating: Minimum IMDb rating filter
        recommendation_service: Recommendation service dependency

    Returns:
        List of trending movie recommendations
    """
    try:
        ***REMOVED*** Use the cached function to get data as dictionary
        data = await _get_trending_recommendations_data(
            limit=limit,
            days=days,
            min_rating=min_rating,
            recommendation_service=recommendation_service,
        )

        ***REMOVED*** Convert dictionary back to Pydantic model for response
        return RecommendationsResponse(**data)

    except SQLAlchemyError as e:
        logger.error(f"Database error getting trending recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        )
    except Exception as e:
        logger.error(f"Error getting trending recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
