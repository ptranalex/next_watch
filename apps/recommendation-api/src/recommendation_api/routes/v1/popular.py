"""Popular movie recommendations endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.db.connection import get_db_session
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    RecommendationsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/popular", response_model=RecommendationsResponse)
async def get_popular_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    session: Session = Depends(get_db_session),
):
    """Get popular movie recommendations.
    
    Args:
        limit: Maximum number of recommendations (1-100)
        min_rating: Minimum IMDb rating (0-10)
        min_vote_count: Minimum vote count threshold
        session: Database session
        
    Returns:
        List of popular movie recommendations
    """
    try:
        service = RecommendationService(session)
        recommendations, filters = service.get_popular_recommendations(
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
            detail="Database service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Error getting popular recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 