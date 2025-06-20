"""Similar movie recommendations endpoints."""

import logging
from typing import Optional, Dict, Any

from cache.decorators import redis_cache
from cache.keys import build_cache_key
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import SQLAlchemyError

from recommendation_api.services.movie_adapter import MovieDataAdapter, get_movie_adapter
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.models.recommendation import (
    MovieRecommendation,
    SimilarMoviesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


***REMOVED*** Custom key builder for similar movies
def _build_similar_movies_key(
    movie_id: int,
    limit: int = 20,
    min_score: float = 0.01,
    movie_adapter: MovieDataAdapter = None,
    **kwargs,
) -> str:
    """Build a custom cache key for similar movies."""
    return build_cache_key(
        "similar", [movie_id, f"limit:{limit}", f"score:{min_score}"], prefix="reco:"
    )


@router.get("/movies/{movie_id}/similar", response_model=SimilarMoviesResponse)
@redis_cache(
    ttl=3600,  ***REMOVED*** 1 hour TTL
    key_builder=_build_similar_movies_key,
    enable_metrics=True,
)
async def get_similar_movies_endpoint(
    movie_id: int,
    limit: int = Query(20, ge=1, le=50),
    min_score: float = Query(0.01, ge=0, le=1.0),
    movie_adapter: MovieDataAdapter = Depends(get_movie_adapter),
) -> Dict[str, Any]:
    """Get movies similar to a specific movie.

    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of similar movies (1-50)
        min_score: Minimum similarity score threshold (0-1)
        movie_adapter: Movie data adapter

    Returns:
        Dictionary containing similar movie recommendations (JSON-serializable)
    """
    try:
        if movie_id <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie ID")

        logger.debug(f"Finding similar movies for movie ID {movie_id} with min_score={min_score}")

        service = RecommendationService(movie_adapter)
        recommendations, filters = await service.get_similar_movies(
            movie_id=movie_id,
            limit=limit,
            min_score=min_score,
        )

        if "error" in filters:
            logger.debug(f"Error finding similar movies: {filters['error']}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=filters["error"])

        logger.debug(f"Found {len(recommendations)} similar movies for movie ID {movie_id}")

        ***REMOVED*** Create the response model
        response = SimilarMoviesResponse(
            recommendations=recommendations,
            total=len(recommendations),
            type="similar",
            movie_id=movie_id,
            filters=filters,
        )

        ***REMOVED*** Convert to JSON-serializable dict for caching
        return response.model_dump(mode="json")

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error getting similar movies for movie {movie_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        )
    except Exception as e:
        logger.error(f"Error getting similar movies for movie {movie_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
