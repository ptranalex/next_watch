"""Home screen routes for BFF API."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from fastapi import APIRouter, Depends, Query
from fast_core.errors.exceptions import ExternalServiceException

from bff_api.dependencies import get_backend_client
from bff_api.schemas.screen_schemas import HomeScreenData
from bff_api.services.clients.facade import BackendClient
from bff_api.core.metrics import get_bff_metrics

logger = get_logger(__name__)
router = APIRouter(tags=["home"])


async def _get_movies(
    backend: BackendClient,
    page: int = 1,
    limit: int = 20,
    featured: Optional[bool] = None,
    sort: Optional[str] = None,
    recommended_for: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get movies from backend with various filters.

    Args:
        backend: Backend client for backend service
        page: Page number for pagination
        limit: Number of items per page
        featured: Filter for featured movies
        sort: Sort order (popularity, release_date, etc.)
        recommended_for: User ID for recommendations
        user_id: User ID for personalized content

    Returns:
        Movies response from backend

    Raises:
        Exception: If request fails
    """
    ***REMOVED*** Use BackendClient.get_movies method instead of direct HTTP calls
    return await backend.get_movies(
        page=page,
        limit=limit,
        user_id=user_id,
        featured=featured,
        sort=sort,
        recommended_for=recommended_for,
    )


async def _get_genres(backend: BackendClient) -> List[Dict[str, Any]]:
    """Get genres from backend.

    Args:
        backend: Backend client for backend service

    Returns:
        List of genres

    Raises:
        Exception: If request fails
    """
    ***REMOVED*** Use BackendClient.get_genres method instead of direct HTTP calls
    return await backend.get_genres()


@router.get("/home", response_model=HomeScreenData)
async def get_home_screen(
    user_id: Optional[int] = Query(None, description="User ID for personalized content"),
    backend: BackendClient = Depends(get_backend_client),
) -> HomeScreenData:
    """Get aggregated data for home screen.

    Fetches and aggregates multiple data sources for the main app home screen
    including featured movies, popular content, recent releases, and
    personalized recommendations if user_id is provided.

    Args:
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Aggregated home screen data with all content sections

    Raises:
        ExternalServiceException: If backend service is unavailable
    """
    ***REMOVED*** Record movie request metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_movie_request("home", "started")

    try:
        ***REMOVED*** Fetch data concurrently (in real implementation, use asyncio.gather)
        featured_movies_response = await _get_movies(
            backend, page=1, limit=10, featured=True, user_id=user_id
        )
        popular_movies_response = await _get_movies(
            backend, page=1, limit=20, sort="popularity", user_id=user_id
        )
        recent_releases_response = await _get_movies(
            backend, page=1, limit=15, sort="release_date", user_id=user_id
        )
        genres = await _get_genres(backend)

        ***REMOVED*** Handle user recommendations
        user_recommendations = []
        if user_id:
            try:
                recommendations_response = await _get_movies(
                    backend, page=1, limit=20, recommended_for=user_id, user_id=user_id
                )
                user_recommendations = recommendations_response.get("results", [])
            except Exception:
                logger.warning(
                    "Failed to get recommendations for user",
                    user_id=user_id,
                    service="bff",
                    endpoint="home_screen",
                )

        ***REMOVED*** Record successful movie request metrics
        if metrics:
            metrics.record_movie_request("home", "success")

        return HomeScreenData(
            featured_movies=featured_movies_response.get("results", []),
            popular_movies=popular_movies_response.get("results", []),
            recent_releases=recent_releases_response.get("results", []),
            user_recommendations=user_recommendations,
            genres=genres,
        )

    except Exception as e:
        ***REMOVED*** Record error metrics
        if metrics:
            metrics.record_movie_request("home", "error")

        logger.error(
            "Backend error for home_screen",
            error=str(e),
            service="bff",
            endpoint="home_screen",
            user_id=user_id,
        )
        raise ExternalServiceException(
            detail="Backend service unavailable",
            service_name="backend-api",
            error_code="SERVICE_UNAVAILABLE",
        )
