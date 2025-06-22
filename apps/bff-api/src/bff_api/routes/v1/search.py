"""Search-related routes for BFF API."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from fastapi import APIRouter, Depends, Query
from fast_core.errors.exceptions import ExternalServiceException
from fast_core.security.rate_limit import rate_limit

from bff_api.dependencies import get_backend_client
from bff_api.services.clients.facade import BackendClient

logger = get_logger(__name__)
router = APIRouter(tags=["search"])


def _build_api_path(path: str) -> str:
    """Build API path with version prefix.

    Args:
        path: Relative API path

    Returns:
        Full API path with version prefix
    """
    ***REMOVED*** Remove leading slash if present to avoid double slashes
    clean_path = path.lstrip("/")
    return f"/api/v1/{clean_path}"


async def _handle_backend_error(e: Exception, operation: str, **context: Any) -> None:
    """Handle backend service errors consistently.

    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        **context: Additional context for logging
    """
    logger.error(
        f"Backend error for {operation}", error=str(e), service="bff", endpoint=operation, **context
    )
    raise ExternalServiceException(
        detail="Backend service unavailable",
        service_name="backend-api",
        error_code="SERVICE_UNAVAILABLE",
    )


@rate_limit(requests=50, window=60)  ***REMOVED*** 50 searches per minute
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

    except Exception as e:
        await _handle_backend_error(e, "search", query=q)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}


@rate_limit(requests=100, window=60)  ***REMOVED*** 100 suggestions per minute (higher for typeahead)
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
        ***REMOVED*** Use the _get_client() method to get the HTTP client
        ***REMOVED*** since suggestion methods are not yet implemented in BackendClient
        client = await backend._get_client()
        response = await client.get(
            _build_api_path("/search/suggestions"),
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        result = cast(Dict[str, Any], response.json())
        return result

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        await _handle_backend_error(e, "search_suggestions", query=query)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}


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
        ***REMOVED*** Use the _get_client() method to get the HTTP client
        ***REMOVED*** since suggestion methods are not yet implemented in BackendClient
        client = await backend._get_client()
        response = await client.get(
            _build_api_path("/search/suggestions/text"),
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        result = cast(Dict[str, Any], response.json())
        return result

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        await _handle_backend_error(e, "text_suggestions", query=query)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}


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
        params: Dict[str, Union[str, int, List[str]]] = {
            "query": query,
            "page": page,
            "limit": limit,
        }
        if types:
            params["types"] = types

        ***REMOVED*** Use the _get_client() method to get the HTTP client
        ***REMOVED*** since this method is not yet implemented in BackendClient
        client = await backend._get_client()
        response = await client.get(
            _build_api_path("/search"),
            params=params,
        )
        response.raise_for_status()
        result = cast(Dict[str, Any], response.json())
        return result

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        await _handle_backend_error(e, "search_all", query=query)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}
