"""Popular movie recommendations endpoints."""

import logging
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


***REMOVED*** Custom key builder for popular movies
def _build_popular_movies_key(
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
    movie_adapter: MovieDataAdapter = None,
    **kwargs,
) -> str:
    """Build a custom cache key for popular movies."""
    return build_cache_key(
        "popular",
        [f"limit:{limit}", f"rating:{min_rating}", f"votes:{min_vote_count}"],
        prefix="reco:",
    )


@router.get("/popular", response_model=RecommendationsResponse)
@redis_cache(
    ttl=1800,  ***REMOVED*** 30 minutes TTL
    key_builder=_build_popular_movies_key,
    enable_metrics=True,
)
async def get_popular_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    movie_adapter: MovieDataAdapter = Depends(get_movie_adapter),
) -> RecommendationsResponse:
    """Get popular movie recommendations.

    Args:
        limit: Maximum number of recommendations (1-100)
        min_rating: Minimum IMDb rating (0-10)
        min_vote_count: Minimum vote count threshold
        movie_adapter: Movie data adapter

    Returns:
        List of popular movie recommendations
    """
    try:
        ***REMOVED*** Create recommendation service
        service = RecommendationService(movie_adapter)

        ***REMOVED*** Use the new direct method instead of the commented-out one
        recommendations, filters = await service.get_popular_recommendations_direct(
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )

        return RecommendationsResponse(
            recommendations=recommendations,
            total=len(recommendations),
            type="popular",
            filters=filters,
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error getting popular recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        )
    except Exception as e:
        logger.error(f"Error getting popular recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
