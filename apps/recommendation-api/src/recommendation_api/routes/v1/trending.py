"""Trending movie recommendations endpoints."""

import logging
from typing import Optional
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


@router.get("/trending", response_model=RecommendationsResponse)
async def get_trending_recommendations_endpoint(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    session: Session = Depends(get_db_session),
):
    """Get trending movie recommendations.
    
    Args:
        limit: Maximum number of recommendations (1-100)
        days: Number of days to look back for trending calculation (1-30)
        min_rating: Minimum IMDb rating filter
        session: Database session
        
    Returns:
        List of trending movie recommendations
    """
    try:
        service = RecommendationService(session)
        recommendations, filters = service.get_trending_recommendations(
            limit=limit,
            days=days,
            min_rating=min_rating,
        )
        
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
            detail="Database service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Error getting trending recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 