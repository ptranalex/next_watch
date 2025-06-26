"""Suggestion routes for Search API v1.

This module contains the suggestion endpoints that were moved from backend-api.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fast_core.security.rate_limit import rate_limit
from config.logging import get_logger

from search_api.services.search_service import SearchService, SearchServiceException
from search_api.schemas.search import SuggestionsResponse, TextSuggestionsResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["suggestions"])


def get_search_service(request: Request) -> SearchService:
    """Get SearchService instance from app state."""
    search_config = getattr(request.app.state, "search_config")
    return SearchService(search_config)


@rate_limit(requests=200, window=60)  ***REMOVED*** 200 suggestions per minute (higher for typeahead)
@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max number of suggestions to return"),
    search_service: SearchService = Depends(get_search_service),
) -> SuggestionsResponse:
    """
    Get basic search suggestions.

    Returns a small set of search suggestions to power typeahead features.
    This endpoint provides fast, basic suggestions for autocomplete functionality.
    """
    try:
        logger.info(f"Basic suggestions request", query=query, limit=limit)

        ***REMOVED*** Use the search service to get suggestions
        result = await search_service.get_suggestions(
            query=query,
            limit=limit,
        )

        logger.info(f"Basic suggestions completed successfully", total=result.total, query=query)

        return result

    except SearchServiceException as e:
        logger.error(f"Search service error: {str(e)}", query=query)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error getting basic suggestions: {str(e)}", query=query, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@rate_limit(requests=200, window=60)  ***REMOVED*** 200 suggestions per minute
@router.get("/suggestions/text", response_model=TextSuggestionsResponse)
async def get_text_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    search_service: SearchService = Depends(get_search_service),
) -> TextSuggestionsResponse:
    """
    Get text-based search suggestions with rich metadata.

    This endpoint provides rich suggestions for movies, actors, and directors
    with additional information for rendering in autocomplete UI elements.

    Returns deduplicated and ranked suggestions from the Redis-powered
    suggestion engine with enhanced metadata and scoring.
    """
    try:
        logger.info(f"Text suggestions request", query=query, limit=limit)

        ***REMOVED*** Use the search service to get text suggestions
        result = await search_service.get_text_suggestions(
            query=query,
            limit=limit,
        )

        logger.info(f"Text suggestions completed successfully", total=result.total, query=query)

        return result

    except SearchServiceException as e:
        logger.error(f"Search service error: {str(e)}", query=query)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error getting text suggestions: {str(e)}", query=query, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
