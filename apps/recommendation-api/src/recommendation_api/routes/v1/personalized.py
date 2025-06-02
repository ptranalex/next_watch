"""Personalized movie recommendations endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.db.connection import get_db_session
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    PersonalizedRecommendationsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/user/{user_id}", response_model=PersonalizedRecommendationsResponse)
async def get_user_recommendations_endpoint(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    session: Session = Depends(get_db_session),
):
    """Get personalized recommendations for a user.
    
    Args:
        user_id: User ID
        limit: Maximum number of recommendations (1-100)
        min_rating: Minimum IMDb rating (0-10)
        min_vote_count: Minimum vote count threshold
        session: Database session
        
    Returns:
        List of personalized movie recommendations
    """
    try:
        service = RecommendationService(session)
        recommendations, filters = service.get_user_recommendations(
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
            detail="Database service temporarily unavailable"
        )
    except ValueError as e:
        logger.error(f"Invalid user ID {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    except Exception as e:
        logger.error(f"Error getting user recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 