"""Search routes for Search API v1.

This module contains the main search endpoints that were moved from backend-api.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fast_core.security.rate_limit import rate_limit
from config.logging import get_logger

from search_api.services.search_service import SearchService, SearchServiceException
from search_api.schemas.search import SearchResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


def get_search_service(request: Request) -> SearchService:
    """Get SearchService instance from app state."""
    search_config = getattr(request.app.state, "search_config")
    return SearchService(search_config)


@rate_limit(requests=100, window=60)  ***REMOVED*** 100 searches per minute
@router.get("", response_model=Dict[str, Any])
async def search_movies(
    q: str = Query(..., description="Search query for movie titles"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title",
        description="Field to sort by (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    imdb_rating: Optional[float] = Query(
        None, ge=0, le=10, description="Filter by minimum IMDb rating"
    ),
    rotten_tomatoes_rating: Optional[int] = Query(
        None, ge=0, le=100, description="Filter by minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: Optional[int] = Query(
        None, ge=0, le=100, description="Filter by minimum Metacritic rating"
    ),
    year: Optional[int] = Query(None, description="Filter by release year"),
    start_year: Optional[int] = Query(None, description="Filter by start year (inclusive)"),
    end_year: Optional[int] = Query(None, description="Filter by end year (inclusive)"),
    user_id: Optional[int] = Query(None, description="User ID for personalized results"),
    search_service: SearchService = Depends(get_search_service),
) -> Dict[str, Any]:
    """
    Search movies by title with pagination and optional filtering.

    Performs case-insensitive partial matching on movie titles and supports
    comprehensive filtering options. This endpoint was moved from backend-api
    to provide dedicated search functionality.
    """
    try:
        logger.info(f"Movie search request", query=q, page=page, limit=limit)

        ***REMOVED*** Use the search service to perform the movie search
        result = await search_service.search_movies(
            query=q,
            page=page,
            limit=limit,
            genre_id=genre_id,
            actor_id=actor_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
        )

        logger.info(f"Movie search completed successfully", total=result.get("total", 0), page=page)

        return result

    except SearchServiceException as e:
        logger.error(f"Search service error: {str(e)}", query=q)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in movie search: {str(e)}", query=q, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@rate_limit(requests=50, window=60)  ***REMOVED*** 50 searches per minute for all entities
@router.get("/all", response_model=SearchResponse)
async def search_all_entities(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results per page"),
    types: Optional[List[str]] = Query(None, description="Entity types to include in results"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search across all entities (movies, actors, genres).

    Returns paginated search results that can be filtered by entity type.
    This provides a unified search interface across all searchable entities.
    """
    try:
        logger.info(f"All entities search request", query=query, types=types)

        ***REMOVED*** Use the search service to perform multi-entity search
        result = await search_service.search_all_entities(
            query=query,
            page=page,
            limit=limit,
            types=types,
        )

        logger.info(
            f"Multi-entity search completed successfully",
            total=result.total,
            page=page,
            types=types,
        )

        return result

    except SearchServiceException as e:
        logger.error(f"Search service error: {str(e)}", query=query)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in multi-entity search: {str(e)}", query=query, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
