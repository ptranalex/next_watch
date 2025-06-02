"""Similar movie recommendations endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.db.connection import get_db_session
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    SimilarMoviesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/similar/{movie_id}", response_model=SimilarMoviesResponse)
async def get_similar_movies_endpoint(
    movie_id: int,
    limit: int = Query(20, ge=1, le=50),
    min_rating: float = Query(7.0, ge=0, le=10),
    min_vote_count: int = Query(1000, ge=0),
    session: Session = Depends(get_db_session),
):
    """Get movies similar to a specific movie.
    
    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of similar movies (1-50)
        min_rating: Minimum IMDb rating (0-10)
        min_vote_count: Minimum vote count threshold
        session: Database session
        
    Returns:
        List of similar movie recommendations
    """
    try:
        if movie_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid movie ID"
            )
            
        service = RecommendationService(session)
        recommendations, filters = service.get_similar_movies(
            movie_id=movie_id,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )
        
        if "error" in filters:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=filters["error"]
            )
        
        return SimilarMoviesResponse(
            recommendations=recommendations,
            total=len(recommendations),
            type="similar",
            movie_id=movie_id,
            filters=filters,
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error getting similar movies for movie {movie_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Error getting similar movies for movie {movie_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 