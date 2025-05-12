"""
Search-related API routes (v1).
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import List, Optional, Dict, Any
import logging
import traceback
import os
from redis.exceptions import RedisError

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db
from backend_api.config.app import settings

***REMOVED*** Import pydantic models for response
from pydantic import BaseModel
from backend_api.schemas.movie_schema import MovieResponse

***REMOVED*** Import the suggestion engine
from backend_api.services.suggestion_engine import SuggestionEngine


class Suggestion(BaseModel):
    id: int
    name: str
    type: str  ***REMOVED*** "movie", "actor", "genre"
    image_path: Optional[str] = None


class TextSuggestion(BaseModel):
    """Enhanced text-based suggestion response model"""

    text: str
    type: str  ***REMOVED*** "movie", "actor", "director"
    id: Optional[int] = None
    image_path: Optional[str] = None
    year: Optional[int] = None  ***REMOVED*** Useful for movies
    popularity: Optional[float] = None
    is_partial: bool = False  ***REMOVED*** Whether this is a partial/incomplete match
    search_type: str = (
        "unknown"  ***REMOVED*** How this suggestion was matched (exact, prefix, word, contains)
    )
    additional_info: Optional[Dict[str, Any]] = None


class SuggestionsResponse(BaseModel):
    suggestions: List[Suggestion]
    total: int


class TextSuggestionsResponse(BaseModel):
    """Response model for text-based suggestions"""

    suggestions: List[TextSuggestion]
    total: int


logger = logging.getLogger(__name__)

***REMOVED*** Initialize suggestion engine with Redis URL (should be configured in settings)
***REMOVED*** This will be initialized properly in the application startup events
suggestion_engine = None


***REMOVED*** Dependency to get suggestion engine
async def get_suggestion_engine() -> SuggestionEngine:
    """
    Get an instance of the SuggestionEngine.

    In a production app, you would initialize this during app startup
    and manage the connection pool lifecycle.
    """
    global suggestion_engine
    if suggestion_engine is None:
        suggestion_engine = SuggestionEngine(settings.redis_url)
        await suggestion_engine.initialize()
    return suggestion_engine


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(
        10, ge=1, le=20, description="Max number of suggestions to return"
    ),
    db: Session = Depends(get_db),
):
    """
    Get search suggestions across all entities based on a query string.

    This returns a small set of search suggestions to power typeahead features.
    """
    try:
        logger.info(f"Getting search suggestions for '{query}'")

        ***REMOVED*** This is a placeholder implementation
        ***REMOVED*** In a real implementation, you would query multiple entity types
        ***REMOVED*** and combine results

        ***REMOVED*** Return an empty response for now
        return SuggestionsResponse(suggestions=[], total=0)
    except Exception as e:
        logger.error(f"Error fetching search suggestions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/suggestions/text", response_model=TextSuggestionsResponse)
async def get_text_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    suggestion_engine: SuggestionEngine = Depends(get_suggestion_engine),
):
    """
    Get text-based search suggestions from Redis based on a query prefix.

    This endpoint provides rich suggestions for movies, actors, and directors
    with additional information for rendering in autocomplete UI elements.

    Returns deduplicated and ranked suggestions, with only one entry per entity
    (choosing the best match) and sorted by relevance score.
    """
    try:
        logger.info(f"Getting ranked text suggestions for '{query}'")

        ***REMOVED*** Get ranked entity suggestions with deduplication
        ranked_suggestions = await suggestion_engine.get_ranked_suggestions(
            query, limit
        )

        ***REMOVED*** Format suggestions
        formatted_suggestions = [
            TextSuggestion(
                text=sugg["text"],
                type=sugg["type"],
                id=sugg.get("id"),
                image_path=sugg.get("image_path"),
                year=sugg.get("year"),
                popularity=sugg.get("popularity"),
                is_partial=sugg.get("is_partial", False),
                search_type=sugg.get("search_type", "unknown"),
                additional_info=sugg.get("additional_info"),
            )
            for sugg in ranked_suggestions
        ]

        return TextSuggestionsResponse(
            suggestions=formatted_suggestions, total=len(formatted_suggestions)
        )

    except RedisError as e:
        logger.error(f"Redis error while getting suggestions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=503, detail="Search suggestion service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Error fetching text suggestions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=SuggestionsResponse)
async def search_all(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results per page"),
    types: List[str] = Query(None, description="Entity types to include in results"),
    db: Session = Depends(get_db),
):
    """
    Search across all entities (movies, actors, genres) with the given query.

    Returns paginated search results that can be filtered by entity type.
    """
    try:
        logger.info(f"Searching for '{query}' with types={types}")

        ***REMOVED*** This is a placeholder implementation
        ***REMOVED*** In a real implementation, you would query multiple entity types
        ***REMOVED*** and combine results based on the requested types

        ***REMOVED*** Return an empty response for now
        return SuggestionsResponse(suggestions=[], total=0)
    except Exception as e:
        logger.error(f"Error searching with query '{query}': {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
