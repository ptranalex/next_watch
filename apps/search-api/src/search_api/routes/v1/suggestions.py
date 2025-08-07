"""Suggestion routes for Search API v1.

This module contains the suggestion endpoints that were moved from backend-api.
"""

from typing import Any, Dict, List, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fast_core.security.rate_limit import rate_limit
from fast_core.responses import ResponseBuilder
from config.logging import get_logger

from search_api.services.search_service import SearchService, SearchServiceException
from search_api.core.metrics import (
    get_search_metrics,
    track_suggestion_operation,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["suggestions"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "search": {
            "include_suggestions": True,
            "include_facets": False,  ***REMOVED*** Not needed for simple suggestions
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


@rate_limit(requests=200, window=60)  ***REMOVED*** 200 suggestions per minute (higher for typeahead)
@router.get("/suggestions")
@track_suggestion_operation
async def get_search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max number of suggestions to return"),
    search_service: SearchService = Depends(get_search_service),
) -> Dict[str, Any]:
    """
    Get basic search suggestions.

    Returns a small set of search suggestions to power typeahead features.
    This endpoint provides fast, basic suggestions for autocomplete functionality.
    """
    try:
        logger.info(f"Basic suggestions request", query=query, limit=limit)

        ***REMOVED*** Record suggestion analytics
        metrics = get_search_metrics()
        if metrics:
            metrics.record_query_pattern("basic_suggestion", len(query))

        ***REMOVED*** Use the search service to get suggestions
        result = await search_service.get_suggestions(
            query=query,
            limit=limit,
        )

        logger.info(f"Basic suggestions completed successfully", total=result.total, query=query)

        ***REMOVED*** Record successful suggestion metrics
        if metrics:
            metrics.record_suggestion_request(
                "basic", "success", 0.0, len(query)
            )  ***REMOVED*** Duration tracked by decorator
            metrics.record_search_request("suggestion", "success", 0.0, result.total)

        ***REMOVED*** Use ResponseBuilder search pattern for consistent response structure
        response = responses.search(
            query=query,
            results=result.suggestions,
            metadata={
                "total": result.total,
                "service_info": {
                    "service_name": "search-api",
                    "search_backend": "redis",
                },
                "api_version": "v1",
                "response_pattern": "search",
                "search_context": {
                    "search_type": "suggestions",
                    "suggestion_type": "basic",
                },
            },
        )
        return cast(Dict[str, Any], response)

    except SearchServiceException as e:
        logger.error(f"Search service error: {str(e)}", query=query)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error getting basic suggestions: {str(e)}", query=query, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@rate_limit(requests=200, window=60)  ***REMOVED*** 200 suggestions per minute
@router.get("/suggestions/text")
@track_suggestion_operation
async def get_text_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    search_service: SearchService = Depends(get_search_service),
) -> Dict[str, Any]:
    """
    Get text-based search suggestions with rich metadata.

    This endpoint provides rich suggestions for movies, actors, and directors
    with additional information for rendering in autocomplete UI elements.

    Returns deduplicated and ranked suggestions from the Redis-powered
    suggestion engine with enhanced metadata and scoring.
    """
    ***REMOVED*** Record suggestion analytics
    metrics = get_search_metrics()
    if metrics:
        metrics.record_query_pattern("text_suggestion", len(query))

    try:
        logger.info(f"Text suggestions request", query=query, limit=limit)

        ***REMOVED*** Use the search service to get text suggestions
        result = await search_service.get_text_suggestions(
            query=query,
            limit=limit,
        )

        logger.info(f"Text suggestions completed successfully", total=result.total, query=query)

        ***REMOVED*** Record successful suggestion metrics
        if metrics:
            metrics.record_suggestion_request("text", "success", 0.0, len(query))
            metrics.record_search_request("suggestion", "success", 0.0, result.total)

        ***REMOVED*** Use ResponseBuilder search pattern for consistent response structure
        response = responses.search(
            query=query,
            results=result.suggestions,
            metadata={
                "total": result.total,
                "service_info": {
                    "service_name": "search-api",
                    "search_backend": "redis",
                },
                "api_version": "v1",
                "response_pattern": "search",
                "search_context": {
                    "search_type": "suggestions",
                    "suggestion_type": "text",
                },
            },
        )
        return cast(Dict[str, Any], response)

    except SearchServiceException as e:
        ***REMOVED*** Record search service errors
        if metrics:
            metrics.record_search_error("service_error", "text_suggestion")
            metrics.record_suggestion_request("text", "error", 0.0, len(query))

        logger.error(f"Search service error: {str(e)}", query=query)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ***REMOVED*** Record unexpected errors
        if metrics:
            metrics.record_search_error("internal_error", "text_suggestion")
            metrics.record_suggestion_request("text", "error", 0.0, len(query))

        logger.error(
            f"Unexpected error getting text suggestions: {str(e)}", query=query, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
