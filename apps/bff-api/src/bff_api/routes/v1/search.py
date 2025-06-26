"""Search-related routes for BFF API."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from fastapi import APIRouter, Depends, Query
from fast_core.errors.exceptions import ExternalServiceException
from fast_core.responses import ResponseBuilder
from fast_core.security.rate_limit import rate_limit

from bff_api.dependencies import get_backend_client, get_search_client
from bff_api.services.clients.facade import BackendClient
from bff_api.services.clients.search import SearchAPIClient

logger = get_logger(__name__)
router = APIRouter(tags=["search"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "search": {
            "include_suggestions": True,
            "include_facets": True,
        },
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)


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

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=results.get("results", []),
            page=page,
            limit=limit,
            total=results.get("total", 0),
            metadata={
                "query": q,
                "search_info": {
                    "query": q,
                    "personalized": bool(user_id),
                    "has_next": results.get("has_next", False),
                },
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "search_context": {"search_type": "movies"},
            },
        )
        return cast(Dict[str, Any], response)

    except Exception as e:
        await _handle_backend_error(e, "search", query=q)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}


@rate_limit(requests=100, window=60)  ***REMOVED*** 100 suggestions per minute (higher for typeahead)
@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Max number of suggestions to return"),
    search_client: SearchAPIClient = Depends(get_search_client),
) -> Dict[str, Any]:
    """Get basic search suggestions.

    Returns a small set of search suggestions to power typeahead features.
    Now uses the dedicated Search API service for better performance.

    Args:
        query: Search query string
        limit: Maximum number of suggestions to return
        search_client: Search API client dependency

    Returns:
        Search suggestions response

    Raises:
        HTTPException: If Search API service is unavailable (502)
    """
    try:
        logger.info(f"Basic suggestions request via Search API", query=query, limit=limit)

        result = await search_client.get_suggestions(
            query=query,
            limit=limit,
        )

        logger.info(
            f"Basic suggestions completed successfully",
            total=result.get("metadata", {}).get("total", 0),
            query=query,
        )

        ***REMOVED*** Use ResponseBuilder search pattern for consistent response structure
        response = responses.search(
            query=query,
            results=result.get("results", []),
            metadata={
                "total": result.get("metadata", {}).get("total", 0),
                "service_info": {
                    "aggregated_from": ["search-api"],
                    "user_authenticated": False,
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

    except Exception as e:
        await _handle_backend_error(e, "search_suggestions", query=query)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}


@router.get("/search/suggestions/text")
async def get_text_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    search_client: SearchAPIClient = Depends(get_search_client),
) -> Dict[str, Any]:
    """Get text-based search suggestions with rich metadata.

    This endpoint provides rich suggestions for movies, actors, and directors
    with additional information for rendering in autocomplete UI elements.

    Returns deduplicated and ranked suggestions from the dedicated Search API's
    Redis-powered suggestion engine with enhanced performance.

    Args:
        query: Search query prefix
        limit: Maximum number of suggestions to return
        search_client: Search API client dependency

    Returns:
        Rich text suggestions with metadata

    Raises:
        HTTPException: If Search API service is unavailable (502)
    """
    try:
        logger.info(f"Text suggestions request via Search API", query=query, limit=limit)

        result = await search_client.get_text_suggestions(
            query=query,
            limit=limit,
        )

        logger.info(
            f"Text suggestions completed successfully",
            total=result.get("metadata", {}).get("total", 0),
            query=query,
        )

        ***REMOVED*** Use ResponseBuilder search pattern for consistent response structure
        response = responses.search(
            query=query,
            results=result.get("results", []),
            metadata={
                "total": result.get("metadata", {}).get("total", 0),
                "service_info": {
                    "aggregated_from": ["search-api"],
                    "user_authenticated": False,
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

    except Exception as e:
        await _handle_backend_error(e, "text_suggestions", query=query)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}


@router.get("/search/all")
async def search_all_entities(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results per page"),
    types: Optional[List[str]] = Query(None, description="Entity types to include in results"),
    search_client: SearchAPIClient = Depends(get_search_client),
) -> Dict[str, Any]:
    """Search across all entities (movies, actors, genres).

    Returns paginated search results that can be filtered by entity type.
    Now uses the dedicated Search API service for better performance.

    Args:
        query: Search query string
        page: Page number for pagination
        limit: Maximum number of results per page
        types: Optional list of entity types to filter by
        search_client: Search API client dependency

    Returns:
        Search results across all entity types

    Raises:
        HTTPException: If Search API service is unavailable (502)
    """
    try:
        logger.info(f"Multi-entity search request via Search API", query=query, types=types)

        result = await search_client.search_all_entities(
            query=query,
            page=page,
            limit=limit,
            types=types,
        )

        logger.info(
            f"Multi-entity search completed successfully",
            total=result.get("pagination", {}).get("total", 0),
            page=page,
            query=query,
            types=types,
        )

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=result.get("results", []),
            page=page,
            limit=limit,
            total=result.get("pagination", {}).get("total", 0),
            metadata={
                "query": query,
                "filters_applied": {
                    "types": types,
                },
                "service_info": {
                    "aggregated_from": ["search-api"],
                    "user_authenticated": False,
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

    except Exception as e:
        await _handle_backend_error(e, "search_all", query=query)
        ***REMOVED*** This line is unreachable but satisfies type checker
        return {}
