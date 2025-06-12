"""Sidebar-related routes for BFF API."""

from typing import Optional, Dict, Any, List, cast
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.schemas.screen_schemas import (
    SidebarData,
    SidebarLinkData,
    SidebarFilters,
    SidebarGenre,
    SidebarMetadata,
)
from bff_api.dependencies.common import get_backend_client
from bff_api.services.backend_client import BackendClient, BackendClientError
from bff_api.config.logging import get_logger

logger = get_logger("bff_api.routes.sidebar")
router = APIRouter(tags=["sidebar"])


@router.get("/sidebar", response_model=SidebarData)
async def get_sidebar_content(
    user_id: Optional[int] = Query(None, description="User ID for personalized sidebar content"),
    backend: BackendClient = Depends(get_backend_client),
) -> SidebarData:
    """Get dynamic sidebar content configuration.

    Provides configurable sidebar structure that can be customized
    based on user authentication status and preferences.
    Includes user lists, top movies, and genre navigation.

    Args:
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Dynamic sidebar configuration with links and metadata

    Raises:
        HTTPException: 502 if backend unavailable
    """
    try:
        ***REMOVED*** Get genres from backend
        logger.info(
            "Fetching genres for sidebar content",
            user_id=user_id,
            service="bff",
            endpoint="sidebar",
        )
        genres = await backend.get_genres()

        ***REMOVED*** Ensure we have a valid list (defensive programming)
        if not genres:
            logger.warning(
                "No genres returned from backend",
                user_id=user_id,
                service="bff",
                endpoint="sidebar",
                component="genre_processing",
            )

        logger.info(
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
                SidebarLinkData(
                    id="watchlist",
                    label="Watch List",
                    href="/watchlist",
                    icon="bookmark",
                ),
                SidebarLinkData(
                    id="watched",
                    label="Watched",
                    href="/watched",
                    icon="eye",
                ),
                SidebarLinkData(
                    id="liked",
                    label="Liked",
                    href="/liked",
                    icon="heart",
                ),
                SidebarLinkData(
                    id="recommended",
                    label="Our Picks",
                    href="/recommended",
                    icon="check-badge",
                ),
            ]

        ***REMOVED*** Build top navigation links
        top_links = [
            SidebarLinkData(
                id="top-current",
                label="Best of Year",
                href="/top/current-year",
                icon="trophy",
            ),
            SidebarLinkData(
                id="top-2024",
                label="Popular in 2024",
                href="/top/2024",
                icon="calendar",
            ),
            SidebarLinkData(
                id="top-2023",
                label="Popular by 2023",
                href="/top/2023",
                icon="calendar",
            ),
            SidebarLinkData(
                id="top-all-time",
                label="All time top",
                href="/top/all-time",
                icon="laurel-crown",
            ),
        ]

        ***REMOVED*** Build filter configuration
        filters = SidebarFilters(
            show=True,
            defaults={
                "rating_imdb": None,
                "year": None,
            },
            locked=[],
        )

        ***REMOVED*** Build genre links
        genre_links = [
            SidebarGenre(
                id=int(genre["id"]) if isinstance(genre["id"], (int, str)) else 0,
                name=str(genre["name"]),
                href=f"/genres/{genre['id']}",
            )
            for genre in genres
        ]
        logger.info(
            "Built genre navigation links for sidebar",
            genre_link_count=len(genre_links),
            user_id=user_id,
            service="bff",
            endpoint="sidebar",
            component="navigation_building",
        )

        ***REMOVED*** Build metadata
        metadata = SidebarMetadata(
            layout="sidebar",
            version="1.0.0",
            user_authenticated=bool(user_id),
        )

        return SidebarData(
            home=home,
            user_links=user_links,
            top_links=top_links,
            filters=filters,
            genres=genre_links,
            metadata=metadata,
        )

    except BackendClientError as e:
        logger.error(
            "Backend error while fetching sidebar content",
            error=str(e),
            user_id=user_id,
            service="bff",
            endpoint="sidebar",
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")
    except Exception as e:
        logger.error(
            "Unexpected error in sidebar endpoint",
            error=str(e),
            user_id=user_id,
            service="bff",
            endpoint="sidebar",
        )
        raise HTTPException(status_code=500, detail="Internal server error")
