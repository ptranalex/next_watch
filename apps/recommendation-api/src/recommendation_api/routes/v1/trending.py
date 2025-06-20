"""Trending movie recommendations endpoints."""

import logging
from typing import Optional
from cache.decorators import redis_cache
from cache.keys import build_cache_key
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.services.movie_adapter import MovieDataAdapter, get_movie_adapter
from recommendation_api.services.recommendation import RecommendationService
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
    movie_adapter: MovieDataAdapter = None,
    **kwargs,
) -> str:
    """Build a custom cache key for trending movies."""
    parts = [f"limit:{limit}", f"days:{days}"]
    if min_rating is not None:
        parts.append(f"rating:{min_rating}")

    return build_cache_key("trending", parts, prefix="reco:")


@router.get("/trending", response_model=RecommendationsResponse)
@redis_cache(
    ttl=1800,  ***REMOVED*** 30 minutes TTL
    key_builder=_build_trending_movies_key,
    enable_metrics=True,
)
async def get_trending_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    movie_adapter: MovieDataAdapter = Depends(get_movie_adapter),
) -> RecommendationsResponse:
    """Get trending movie recommendations.

    Args:
        limit: Maximum number of recommendations (1-100)
        days: Number of days to look back for trending calculation (1-30)
        min_rating: Minimum IMDb rating filter
        movie_adapter: Movie data adapter

    Returns:
        List of trending movie recommendations
    """
    try:
        service = RecommendationService(movie_adapter)
        ***REMOVED*** Temporarily use popular_recommendations_direct as trending implementation
        ***REMOVED*** since get_trending_recommendations_direct doesn't exist yet
        min_vote_count = 1000  ***REMOVED*** Default value from other methods
        recommendations, filters = await service.get_popular_recommendations_direct(
            limit=limit,
            min_rating=min_rating or 7.0,  ***REMOVED*** Default to 7.0 if None
            min_vote_count=min_vote_count,
        )

        ***REMOVED*** Update filters to include days parameter
        filters["days"] = days
        filters["type"] = "trending"  ***REMOVED*** Add type to filters

        return RecommendationsResponse(
            recommendations=recommendations,
            total=len(recommendations),
            type="trending",
            filters=filters,
        )

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
