"""Sidebar-related routes for BFF API."""

from typing import Any

from cache.decorators import redis_cache
from cache.keys import build_cache_key
from config.logging import get_logger
from fast_core.errors.exceptions import ExternalServiceException
from fastapi import APIRouter, Depends, Query

from bff_api.core.metrics import get_bff_metrics
from bff_api.dependencies import get_backend_client
from bff_api.schemas.screen_schemas import (
    SidebarData,
)
from bff_api.services.clients.facade import BackendClient

logger = get_logger(__name__)
router = APIRouter(tags=["sidebar"])


async def _get_genres(backend: BackendClient) -> list[dict[str, Any]]:
    """Get genres from backend.

    Args:
        backend: BackendClient for backend service

    Returns:
        List of genres

    Raises:
        Exception: If backend request fails
    """
    ***REMOVED*** Use BackendClient.get_genres method instead of direct HTTP calls
    return await backend.get_genres()


@redis_cache(
    ttl=3600,  ***REMOVED*** 1 hour - sidebar content changes infrequently
    key_builder=lambda user_id, backend: build_cache_key(
        "sidebar:content", ["user", user_id or "anon"], prefix=""
    ),
)
async def _get_sidebar_content_data(
    user_id: int | None,
    backend: BackendClient,
) -> dict[str, Any]:
    """Internal cached function for sidebar content aggregation."""
    logger.debug(
        "Building sidebar content data",
        user_id=user_id,
        service="bff",
        component="sidebar_data",
    )

    ***REMOVED*** Get genres from backend
    logger.debug(
        "Fetching genres for sidebar content",
        user_id=user_id,
        service="bff",
        endpoint="sidebar",
    )
    genres = await _get_genres(backend)

    ***REMOVED*** Ensure we have a valid list (defensive programming)
    if not genres:
        logger.warning(
            "No genres returned from backend",
            user_id=user_id,
            service="bff",
            endpoint="sidebar",
            component="genre_processing",
        )

    logger.debug(
        "Successfully processed genres for sidebar",
        genre_count=len(genres),
        user_id=user_id,
        service="bff",
        endpoint="sidebar",
    )

    ***REMOVED*** Build home link
    home = {
        "label": "Home",
        "href": "/",
    }

    ***REMOVED*** Build user-specific navigation links
    user_links = []
    if user_id:
        ***REMOVED*** Authenticated user links
        user_links = [
            {
                "id": "watchlist",
                "label": "Watch List",
                "href": "/watchlist",
                "icon": "bookmark",
            },
            {
                "id": "watched",
                "label": "Watched",
                "href": "/watched",
                "icon": "eye",
            },
            {
                "id": "liked",
                "label": "Liked",
                "href": "/liked",
                "icon": "heart",
            },
            {
                "id": "recommended",
                "label": "Our Picks",
                "href": "/recommended",
                "icon": "check-badge",
            },
        ]

    ***REMOVED*** Build top navigation links
    top_links = [
        {
            "id": "top-current",
            "label": "Best of Year",
            "href": "/top/current-year",
            "icon": "trophy",
        },
        {
            "id": "top-2024",
            "label": "Popular in 2024",
            "href": "/top/2024",
            "icon": "calendar",
        },
        {
            "id": "top-2023",
            "label": "Popular by 2023",
            "href": "/top/2023",
            "icon": "calendar",
        },
        {
            "id": "top-all-time",
            "label": "All time top",
            "href": "/top/all-time",
            "icon": "laurel-crown",
        },
    ]

    ***REMOVED*** Build filter configuration
    filters = {
        "show": True,
        "defaults": {
            "rating_imdb": None,
            "year": None,
        },
        "locked": [],
    }

    ***REMOVED*** Build genre links
    genre_links = [
        {
            "id": int(genre["id"]) if isinstance(genre["id"], (int, str)) else 0,
            "name": str(genre["name"]),
            "href": f"/genres/{genre['id']}",
        }
        for genre in genres
    ]
    logger.debug(
        "Built genre navigation links for sidebar",
        genre_link_count=len(genre_links),
        user_id=user_id,
        service="bff",
        endpoint="sidebar",
        component="navigation_building",
    )

    ***REMOVED*** Build metadata
    metadata = {
        "layout": "sidebar",
        "version": "1.0.0",
        "user_authenticated": bool(user_id),
    }

    ***REMOVED*** Return as dictionary for caching
    sidebar_data = {
        "home": home,
        "user_links": user_links,
        "top_links": top_links,
        "filters": filters,
        "genres": genre_links,
        "metadata": metadata,
    }

    logger.debug(
        "Successfully built sidebar content data",
        user_id=user_id,
        service="bff",
        component="sidebar_data",
    )

    return sidebar_data


@router.get("/sidebar", response_model=SidebarData)
async def get_sidebar_content(
    user_id: int | None = Query(
        None, description="User ID for personalized sidebar content"
    ),
    backend: BackendClient = Depends(get_backend_client),
) -> SidebarData:
    """Get dynamic sidebar content configuration.

    Provides configurable sidebar structure that can be customized
    based on user authentication status and preferences.
    Includes user lists, top movies, and genre navigation.

    Args:
        user_id: Optional user ID for personalized content
        backend: BackendClient dependency

    Returns:
        Dynamic sidebar configuration with links and metadata

    Raises:
        ExternalServiceException: If backend unavailable
    """
    ***REMOVED*** Record user action metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_user_action("sidebar_view")

    logger.info(
        "Processing sidebar content request",
        user_id=user_id,
        service="bff",
        endpoint="sidebar",
    )

    try:
        ***REMOVED*** Use the cached function - decorator handles all cache logic
        sidebar_data_dict = await _get_sidebar_content_data(user_id, backend)

        ***REMOVED*** Convert dictionary back to Pydantic model
        return SidebarData(**sidebar_data_dict)

    except Exception as e:
        logger.error(
            "Backend error for sidebar_content",
            error=str(e),
            service="bff",
            endpoint="sidebar_content",
            user_id=user_id,
        )
        raise ExternalServiceException(
            detail="Backend service unavailable",
            service_name="backend-api",
            error_code="SERVICE_UNAVAILABLE",
        )
