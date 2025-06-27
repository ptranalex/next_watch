"""Similar movie recommendations endpoints."""

import logging
from typing import Optional, Dict, Any

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
    SimilarMoviesResponse,
)
from recommendation_api.core.metrics import (
    get_recommendation_metrics,
    track_similar_recommendation,
)

logger = logging.getLogger(__name__)

router = APIRouter()


***REMOVED*** Custom key builder for similar movies
def _build_similar_movies_key(
    movie_id: int,
    limit: int = 20,
    min_score: float = 0.01,
    recommendation_service: RecommendationService = None,
    **kwargs,
) -> str:
    """Build a custom cache key for similar movies."""
    return build_cache_key(
        "similar", [movie_id, f"limit:{limit}", f"score:{min_score}"], prefix="reco:"
    )


@redis_cache(
    ttl=3600,  ***REMOVED*** 1 hour TTL
    key_builder=_build_similar_movies_key,
    enable_metrics=True,
)
async def _get_similar_movies_data(
    movie_id: int,
    limit: int,
    min_score: float,
    recommendation_service: RecommendationService,
) -> Dict[str, Any]:
    """Internal cached function for similar movies data.

    This function returns a dictionary that can be JSON serialized for caching.
    Following the BFF pattern: cached functions return dicts, endpoints return Pydantic models.
    """
    if movie_id <= 0:
        raise ValueError("Invalid movie ID")

    logger.debug(f"Finding similar movies for movie ID {movie_id} with min_score={min_score}")

    recommendations, filters = await recommendation_service.get_similar_movies(
        movie_id=movie_id,
        limit=limit,
        min_score=min_score,
    )

    if "error" in filters:
        logger.debug(f"Error finding similar movies: {filters['error']}")
        raise ValueError(filters["error"])

    logger.debug(f"Found {len(recommendations)} similar movies for movie ID {movie_id}")

    ***REMOVED*** Convert MovieRecommendation objects to dictionaries for caching
    ***REMOVED*** Use mode="json" to ensure proper serialization of date objects
    recommendations_dicts = [rec.model_dump(mode="json") for rec in recommendations]

    ***REMOVED*** Return as dictionary for caching
    return {
        "recommendations": recommendations_dicts,
        "total": len(recommendations),
        "type": "similar",
        "movie_id": movie_id,
        "filters": filters,
    }


@router.get("/movies/{movie_id}/similar", response_model=SimilarMoviesResponse)
@track_similar_recommendation
async def get_similar_movies_endpoint(
    movie_id: int,
    limit: int = Query(20, ge=1, le=50),
    min_score: float = Query(0.01, ge=0, le=1.0),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> SimilarMoviesResponse:
    """Get movies similar to a specific movie.

    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of similar movies (1-50)
        min_score: Minimum similarity score threshold (0-1)
        recommendation_service: Recommendation service dependency

    Returns:
        Similar movie recommendations
    """
    ***REMOVED*** Record recommendation request metrics
    metrics = get_recommendation_metrics()
    if metrics:
        ***REMOVED*** Record filter usage for similar movies
        metrics.record_recommendation_filter_usage(
            "min_score", _categorize_similarity_score(min_score)
        )
        metrics.record_recommendation_filter_usage("limit", _categorize_limit(limit))

    try:
        ***REMOVED*** Use the cached function to get data as dictionary
        data = await _get_similar_movies_data(
            movie_id=movie_id,
            limit=limit,
            min_score=min_score,
            recommendation_service=recommendation_service,
        )

        ***REMOVED*** Record successful similar movies request
        if metrics:
            metrics.record_recommendation_request("similar", "success", 0.0, data.get("total", 0))
            metrics.record_vector_operation("search_similar", "success", 0.0)

        ***REMOVED*** Convert dictionary back to Pydantic model for response
        return SimilarMoviesResponse(**data)

    except ValueError as e:
        ***REMOVED*** Record similar movies failure
        if metrics:
            failure_reason = "invalid_movie_id" if "Invalid movie ID" in str(e) else "not_found"
            metrics.record_recommendation_request("similar", "failure", 0.0, 0)
            metrics.record_vector_operation("search_similar", "failure", 0.0)

        ***REMOVED*** Handle business logic errors (invalid movie ID, not found, etc.)
        if "Invalid movie ID" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError as e:
        ***REMOVED*** Record database error
        if metrics:
            metrics.record_recommendation_request("similar", "failure", 0.0, 0)

        logger.error(f"Database error getting similar movies for movie {movie_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        )
    except Exception as e:
        ***REMOVED*** Record general error
        if metrics:
            metrics.record_recommendation_request("similar", "failure", 0.0, 0)

        logger.error(f"Error getting similar movies for movie {movie_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


def _categorize_similarity_score(score: float) -> str:
    """Categorize similarity score for metrics."""
    if score < 0.1:
        return "very_low"
    elif score < 0.3:
        return "low"
    elif score < 0.6:
        return "medium"
    else:
        return "high"


def _categorize_limit(limit: int) -> str:
    """Categorize limit for metrics."""
    if limit <= 10:
        return "small"
    elif limit <= 30:
        return "medium"
    else:
        return "large"
