"""Personalized movie recommendations endpoints."""

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
    PersonalizedRecommendationsResponse,
)

logger = logging.getLogger(__name__)

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
async def get_personalized_recommendations_endpoint(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> PersonalizedRecommendationsResponse:
    """Get personalized movie recommendations for a user.

    Args:
        user_id: User ID to get recommendations for
        limit: Maximum number of recommendations (1-100)
        min_rating: Minimum IMDb rating filter
        min_vote_count: Minimum vote count filter
        recommendation_service: Recommendation service dependency

    Returns:
        Personalized movie recommendations for the user
    """
    try:
        ***REMOVED*** Use the cached function to get data as dictionary
        data = await _get_personalized_recommendations_data(
            user_id=user_id,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
            recommendation_service=recommendation_service,
        )

        ***REMOVED*** Convert dictionary back to Pydantic model for response
        return PersonalizedRecommendationsResponse(**data)

    except ValueError as e:
        ***REMOVED*** Handle business logic errors (invalid user ID, etc.)
        if "Invalid user ID" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error getting personalized recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        )
    except Exception as e:
        logger.error(
            f"Error getting personalized recommendations for user {user_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
