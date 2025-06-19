"""Search-related routes for BFF API."""

from typing import Any, Dict, List, Optional

from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.dependencies.common import get_backend_client
from bff_api.services.backend_client import BackendClient, BackendClientError

logger = get_logger(__name__)
router = APIRouter(tags=["search"])


@router.get("/search")
async def search_screen(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="User ID for personalized content"),
    backend: BackendClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Get search results for search screen.

    Performs search across movies and returns paginated results with
    optional user personalization for ranking.

    Args:
        q: Search query string
        page: Page number for pagination
        limit: Number of items per page
        user_id: Optional user ID for personalized results
        backend: Backend client dependency

    Returns:
        Search results with pagination metadata

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    try:
        results = await backend.search_movies(
            query=q,
            page=page,
            limit=limit,
            user_id=user_id,
        )

        return {
            "query": q,
            "results": results.get("results", []),
            "total_count": results.get("total", 0),
            "page": page,
            "has_next": results.get("has_next", False),
        }

    except BackendClientError as e:
        logger.error(
            "Backend error for search", query=q, error=str(e), service="bff", endpoint="search"
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Max number of suggestions to return"),
    backend: BackendClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Get basic search suggestions.

    Returns a small set of search suggestions to power typeahead features.

    Args:
        query: Search query string
        limit: Maximum number of suggestions to return
        backend: Backend client dependency

    Returns:
        Search suggestions response

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    try:
        response = await backend._make_request(
            "GET",
            backend._build_api_path("/search/suggestions"),
            params={"query": query, "limit": limit},
        )
        return response

    except BackendClientError as e:
        logger.error(
            "Backend error for search suggestions",
            query=query,
            error=str(e),
            service="bff",
            endpoint="search_suggestions",
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/search/suggestions/text")
async def get_text_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    backend: BackendClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Get text-based search suggestions with rich metadata.

    This endpoint provides rich suggestions for movies, actors, and directors
    with additional information for rendering in autocomplete UI elements.

    Returns deduplicated and ranked suggestions from the backend's Redis-powered
    suggestion engine.

    Args:
        query: Search query prefix
        limit: Maximum number of suggestions to return
        backend: Backend client dependency

    Returns:
        Rich text suggestions with metadata

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    try:
        response = await backend._make_request(
            "GET",
            backend._build_api_path("/search/suggestions/text"),
            params={"query": query, "limit": limit},
        )
        return response

    except BackendClientError as e:
        logger.error(
            "Backend error for text suggestions",
            query=query,
            error=str(e),
            service="bff",
            endpoint="text_suggestions",
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/search/all")
async def search_all_entities(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results per page"),
    types: Optional[List[str]] = Query(None, description="Entity types to include in results"),
    backend: BackendClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Search across all entities (movies, actors, genres).

    Returns paginated search results that can be filtered by entity type.

    Args:
        query: Search query string
        page: Page number for pagination
        limit: Maximum number of results per page
        types: Optional list of entity types to filter by
        backend: Backend client dependency

    Returns:
        Search results across all entity types

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    try:
        params = {"query": query, "page": page, "limit": limit}
        if types:
            params["types"] = types

        response = await backend._make_request(
            "GET", backend._build_api_path("/search"), params=params
        )
        return response

    except BackendClientError as e:
        logger.error(
            "Backend error for all entities search",
            query=query,
            error=str(e),
            service="bff",
            endpoint="search_all",
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")
