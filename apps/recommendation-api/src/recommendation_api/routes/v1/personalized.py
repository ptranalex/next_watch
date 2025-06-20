"""Personalized movie recommendations endpoints."""

import logging
from cache.decorators import redis_cache
from cache.keys import build_cache_key
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.services.movie_adapter import MovieDataAdapter, get_movie_adapter
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    PersonalizedRecommendationsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


***REMOVED*** Custom key builder for personalized recommendations
def _build_personalized_movies_key(
    user_id: int,
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
    movie_adapter: MovieDataAdapter = None,
    **kwargs,
) -> str:
    """Build a custom cache key for personalized movie recommendations."""
    return build_cache_key(
        "personalized",
        [f"user:{user_id}", f"limit:{limit}", f"rating:{min_rating}", f"votes:{min_vote_count}"],
        prefix="reco:",
    )


@router.get("/user/{user_id}", response_model=PersonalizedRecommendationsResponse)
@redis_cache(
    ttl=1800,  ***REMOVED*** 30 minutes TTL
    key_builder=_build_personalized_movies_key,
    enable_metrics=True,
)
async def get_user_recommendations_endpoint(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    movie_adapter: MovieDataAdapter = Depends(get_movie_adapter),
) -> PersonalizedRecommendationsResponse:
    """Get personalized recommendations for a user.

    Args:
        user_id: User ID
        limit: Maximum number of recommendations (1-100)
        min_rating: Minimum IMDb rating (0-10)
        min_vote_count: Minimum vote count threshold
        movie_adapter: Movie data adapter

    Returns:
        List of personalized movie recommendations
    """
    try:
        service = RecommendationService(movie_adapter)

        ***REMOVED*** Use the new direct method instead of the commented-out one
        recommendations, filters = await service.get_user_recommendations_direct(
            user_id=user_id,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )

        return PersonalizedRecommendationsResponse(
            recommendations=recommendations,
            total=len(recommendations),
            type="personalized",
            user_id=user_id,
            filters=filters,
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error getting user recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        )
    except ValueError as e:
        logger.error(f"Invalid user ID {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    except Exception as e:
        logger.error(f"Error getting user recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
