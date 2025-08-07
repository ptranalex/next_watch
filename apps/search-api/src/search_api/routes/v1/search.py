"""Search routes for Search API v1.

This module contains the main search endpoints that were moved from backend-api.
"""

from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fast_core.security.rate_limit import rate_limit
from fast_core.responses import ResponseBuilder
from config.logging import get_logger

from search_api.services.search_service import SearchService, SearchServiceException
from search_api.core.metrics import (
    get_search_metrics,
    track_movie_search,
    track_entity_search,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["search"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
        "search": {
            "include_suggestions": True,
            "include_facets": True,
        },
    }
)


def get_search_service(request: Request) -> SearchService:
    """Get SearchService instance from app state."""
    search_config = getattr(request.app.state, "search_config")

    ***REMOVED*** Create SearchService with shared suggestion engine from app state
    search_service = SearchService(search_config)

    ***REMOVED*** Use the global suggestion engine instance if available
    if hasattr(request.app.state, "suggestion_engine") and request.app.state.suggestion_engine:
        search_service.suggestion_engine = request.app.state.suggestion_engine

    return search_service


@rate_limit(requests=100, window=60)  ***REMOVED*** 100 searches per minute
@router.get("")
@track_movie_search
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

        ***REMOVED*** Record search analytics
        metrics = get_search_metrics()
        if metrics:
            ***REMOVED*** Count applied filters for metrics
            filters_count = sum(
                [
                    1
                    for x in [
                        genre_id,
                        actor_id,
                        imdb_rating,
                        rotten_tomatoes_rating,
                        metacritic_rating,
                        year,
                        start_year,
                        end_year,
                    ]
                    if x is not None
                ]
            )
            metrics.record_query_pattern("movie_search", len(q))
            metrics.record_pagination_usage(page, limit)
            for filter_type, filter_value in [
                ("genre", genre_id),
                ("actor", actor_id),
                ("year", year),
                ("imdb_rating", imdb_rating),
                ("rt_rating", rotten_tomatoes_rating),
                ("metacritic_rating", metacritic_rating),
            ]:
                if filter_value is not None:
                    metrics.record_filter_usage(filter_type, filter_value)

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

        ***REMOVED*** Record successful search metrics
        if metrics:
            total_results = result.get("total", 0)
            metrics.record_search_request(
                "movie", "success", 0.0, total_results
            )  ***REMOVED*** Duration tracked by decorator
            metrics.record_entity_search("movie", "moderate", 0.0)  ***REMOVED*** Duration tracked by decorator

            ***REMOVED*** Record result quality metrics
            if total_results > 0:
                ***REMOVED*** Estimate search quality based on result count and query length
                quality_score = min(1.0, total_results / (len(q) * 10))  ***REMOVED*** Simple heuristic
                metrics.record_search_quality("relevance_score", quality_score)

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=result.get("results", []),
            page=page,
            limit=limit,
            total=result.get("total", 0),
            metadata={
                "query": q,
                "filters_applied": {
                    "genre_id": genre_id,
                    "actor_id": actor_id,
                    "sort_by": sort_by,
                    "sort_desc": sort_desc,
                    "imdb_rating": imdb_rating,
                    "rotten_tomatoes_rating": rotten_tomatoes_rating,
                    "metacritic_rating": metacritic_rating,
                    "year": year,
                    "start_year": start_year,
                    "end_year": end_year,
                },
                "service_info": {
                    "service_name": "search-api",
                    "search_backend": "backend-api",
                    "user_personalized": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "search_context": {
                    "search_type": "movies",
                    "personalized": bool(user_id),
                },
            },
        )
        return cast(Dict[str, Any], response)

    except SearchServiceException as e:
        ***REMOVED*** Record search service errors
        if metrics:
            metrics.record_search_error("service_error", "movie")
            metrics.record_search_request("movie", "error", 0.0, 0)

        logger.error(f"Search service error: {str(e)}", query=q)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ***REMOVED*** Record unexpected errors
        if metrics:
            metrics.record_search_error("internal_error", "movie")
            metrics.record_search_request("movie", "error", 0.0, 0)

        logger.error(f"Unexpected error in movie search: {str(e)}", query=q, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@rate_limit(requests=50, window=60)  ***REMOVED*** 50 searches per minute for all entities
@router.get("/all")
@track_entity_search
async def search_all_entities(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results per page"),
    types: Optional[List[str]] = Query(None, description="Entity types to include in results"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    search_service: SearchService = Depends(get_search_service),
) -> Dict[str, Any]:
    """Search across all entities (movies, actors, genres).

    Returns paginated search results that can be filtered by entity type.
    This provides a unified search interface across all searchable entities.
    """
    ***REMOVED*** Record search analytics
    metrics = get_search_metrics()
    if metrics:
        metrics.record_query_pattern("all_entities_search", len(query))
        metrics.record_pagination_usage(page, limit)
        if types:
            for entity_type in types:
                metrics.record_filter_usage("entity_type", entity_type)

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

        ***REMOVED*** Record successful search metrics
        if metrics:
            metrics.record_search_request("all_entities", "success", 0.0, result.total)
            metrics.record_entity_search("all_entities", "moderate", 0.0)

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=result.suggestions,  ***REMOVED*** Note: search_all_entities returns SearchResponse with suggestions field
            page=page,
            limit=limit,
            total=result.total,
            metadata={
                "query": query,
                "filters_applied": {
                    "types": types,
                    "sort_by": sort_by,
                    "sort_desc": sort_desc,
                },
                "service_info": {
                    "service_name": "search-api",
                    "search_backend": "redis",
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "search_context": {
                    "search_type": "all_entities",
                    "entity_types": types,
                },
            },
        )
        return cast(Dict[str, Any], response)

    except SearchServiceException as e:
        ***REMOVED*** Record search service errors
        if metrics:
            metrics.record_search_error("service_error", "all_entities")
            metrics.record_search_request("all_entities", "error", 0.0, 0)

        logger.error(f"Search service error: {str(e)}", query=query)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ***REMOVED*** Record unexpected errors
        if metrics:
            metrics.record_search_error("internal_error", "all_entities")
            metrics.record_search_request("all_entities", "error", 0.0, 0)

        logger.error(
            f"Unexpected error in multi-entity search: {str(e)}", query=query, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
