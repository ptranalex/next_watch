"""
Search-related API routes (v1).
"""

from typing import Any

from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session

from backend_api.core.metrics import get_backend_metrics
from backend_api.db.database import get_db
from backend_api.queries.movie_query import MovieQuery
from backend_api.schemas.search import SearchResponse

***REMOVED*** Note: Backend API focuses on core data - no suggestion engine


class Suggestion(BaseModel):
    id: int
    name: str
    type: str  ***REMOVED*** "movie", "actor", "genre"
    image_path: str | None = None


class TextSuggestion(BaseModel):
    """Enhanced text-based suggestion response model"""

    text: str
    type: str  ***REMOVED*** "movie", "actor", "director"
    id: int | None = None
    image_path: str | None = None
    year: int | None = None  ***REMOVED*** Useful for movies
    popularity: float | None = None
    is_partial: bool = False  ***REMOVED*** Whether this is a partial/incomplete match
    search_type: str = "unknown"  ***REMOVED*** How this suggestion was matched (exact, prefix, word, contains)
    additional_info: dict[str, Any] | None = None


class SuggestionsResponse(BaseModel):
    suggestions: list[Suggestion]
    total: int


class TextSuggestionsResponse(BaseModel):
    """Response model for text-based suggestions"""

    suggestions: list[TextSuggestion]
    total: int


logger = get_logger(__name__)

***REMOVED*** Backend API provides basic search functionality via database queries


***REMOVED*** Backend API focuses on core data - suggestion engine moved to recommendation service


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Max number of suggestions to return"),
    db: Session = Depends(get_db),
) -> SuggestionsResponse:
    """
    Get search suggestions across all entities based on a query string.

    This returns a small set of search suggestions to power typeahead features.
    """
    ***REMOVED*** Record metrics
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_movie_search("suggestions", 0, 0.0)  ***REMOVED*** No filters, placeholder duration

    try:
        logger.debug(f"Getting search suggestions for '{query}'")

        ***REMOVED*** This is a placeholder implementation
        ***REMOVED*** In a real implementation, you would query multiple entity types
        ***REMOVED*** and combine results

        ***REMOVED*** Return an empty response for now
        return SuggestionsResponse(suggestions=[], total=0)
    except Exception as e:
        ***REMOVED*** Record error metrics
        if metrics:
            metrics.record_movie_search("suggestions_error", 0, 0.0)
        logger.error(f"Error fetching search suggestions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/suggestions/text", response_model=TextSuggestionsResponse)
async def get_text_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    db: Session = Depends(get_db),
) -> TextSuggestionsResponse:
    """
    Get text-based search suggestions based on database queries.

    This endpoint provides basic suggestions for movies using direct database queries.
    For advanced suggestions with Redis caching, use the recommendation service.
    """
    try:
        logger.debug(f"Getting basic text suggestions for '{query}' from database")

        ***REMOVED*** Use MovieQuery to search for movies that match the query
        movie_query = MovieQuery()
        movies, _ = movie_query.search_movies_by_title(db, title_search=query, skip=0, limit=limit)

        ***REMOVED*** Format as suggestions
        formatted_suggestions = []
        for movie in movies:
            ***REMOVED*** Extract movie title and basic info
            if isinstance(movie, dict):
                title = str(movie.get("title") or "Unknown")
                movie_id = movie.get("id")
                release_date = movie.get("release_date")
            else:
                title = getattr(movie, "title", "Unknown")
                movie_id = getattr(movie, "id", None)
                release_date = getattr(movie, "release_date", None)

            year = None
            if release_date and hasattr(release_date, "year"):
                year = release_date.year

            formatted_suggestions.append(
                TextSuggestion(
                    text=title,
                    type="movie",
                    id=movie_id,
                    year=year,
                    search_type="title_match",
                    is_partial=len(query) < len(title),
                )
            )

        return TextSuggestionsResponse(
            suggestions=formatted_suggestions, total=len(formatted_suggestions)
        )

    except Exception as e:
        logger.error(f"Error fetching text suggestions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=SearchResponse)
async def search_all(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results per page"),
    types: list[str] = Query(None, description="Entity types to include in results"),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """
    Search across all entities (movies, actors, genres) with the given query.

    Returns paginated search results that can be filtered by entity type.
    """
    try:
        logger.debug(f"Searching for '{query}' with types={types}")

        ***REMOVED*** This is a placeholder implementation
        ***REMOVED*** In a real implementation, you would query multiple entity types
        ***REMOVED*** and combine results based on the requested types

        ***REMOVED*** Return an empty response for now
        return SearchResponse(
            suggestions=[],
            total=0,
            page=page,
            per_page=limit,
            total_pages=0,
            has_next=False,
            has_prev=False,
        )
    except Exception as e:
        logger.error(f"Error searching with query '{query}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
