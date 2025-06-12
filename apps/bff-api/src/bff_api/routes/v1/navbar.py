"""Navbar-related routes for BFF API."""

from typing import Optional, List, Dict, Any, cast
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.schemas.screen_schemas import NavbarData, NavbarLinkData
from bff_api.dependencies.common import get_backend_client
from bff_api.services.backend_client import BackendClient, BackendClientError
from bff_api.config.logging import get_logger

logger = get_logger("bff_api.routes.navbar")
router = APIRouter(tags=["navbar"])


@router.get("/navbar", response_model=NavbarData)
async def get_navbar_content(
    user_id: Optional[int] = Query(None, description="User ID for personalized navbar content"),
    section: Optional[str] = Query(None, description="App section for context-aware navigation"),
    backend: BackendClient = Depends(get_backend_client),
) -> NavbarData:
    """Get dynamic navbar content configuration.

    Provides configurable navigation structure that can be customized
    based on user authentication status, preferences, and current app section.
    For migration, returns genre-based navigation links.

    Args:
        user_id: Optional user ID for personalized content
        section: Optional app section for context-aware navigation
        backend: Backend client dependency

    Returns:
        Dynamic navbar configuration with links and metadata

    Raises:
        HTTPException: 502 if backend unavailable
    """
    try:
        ***REMOVED*** Get genres from backend for migration (genre nav links)
        genres_response = await backend.get_genres()
        ***REMOVED*** Handle the case where genres_response is a list directly
        if isinstance(genres_response, list):
            genres = genres_response
        else:
            ***REMOVED*** If it's a dict, try to get the results key
            genres = genres_response.get("results", []) if isinstance(genres_response, dict) else []

        ***REMOVED*** Build brand configuration
        brand = {
            "name": "Next Watch",
            "logo": "/logo.png",
            "href": "/",
        }

        ***REMOVED*** Build primary navigation links (genre-based for migration)
        primary_links = []

        ***REMOVED*** Add home link
        primary_links.append(
            NavbarLinkData(
                id="home",
                label="Home",
                href="/",
                icon="home",
                order=0,
                is_active=section == "home",
            )
        )

        ***REMOVED*** Add genre links for migration
        for i, genre in enumerate(genres[:8]):  ***REMOVED*** Limit to 8 genres for navbar
            primary_links.append(
                NavbarLinkData(
                    id=f"genre-{genre['id']}",
                    label=genre["name"],
                    href=f"/genres/{genre['id']}",
                    order=i + 1,
                    is_active=section == f"genre-{genre['id']}",
                    metadata={"genre_id": genre["id"]},
                )
            )

        ***REMOVED*** Build secondary navigation links
        secondary_links = [
            NavbarLinkData(
                id="search",
                label="Search",
                href="/search",
                icon="search",
                order=0,
                is_active=section == "search",
            ),
            NavbarLinkData(
                id="discover",
                label="Discover",
                href="/discover",
                icon="compass",
                order=1,
                is_active=section == "discover",
            ),
        ]

        ***REMOVED*** Build user-specific navigation links
        user_links = []
        if user_id:
            ***REMOVED*** Authenticated user links
            user_links = [
                NavbarLinkData(
                    id="watchlist",
                    label="Watchlist",
                    href="/watchlist",
                    icon="bookmark",
                    order=0,
                    is_active=section == "watchlist",
                ),
                NavbarLinkData(
                    id="liked",
                    label="Liked",
                    href="/liked",
                    icon="heart",
                    order=1,
                    is_active=section == "liked",
                ),
                NavbarLinkData(
                    id="watched",
                    label="Watched",
                    href="/watched",
                    icon="check",
                    order=2,
                    is_active=section == "watched",
                ),
                NavbarLinkData(
                    id="profile",
                    label="Profile",
                    href="/profile",
                    icon="user",
                    order=3,
                    is_active=section == "profile",
                ),
            ]
        else:
            ***REMOVED*** Guest user links
            user_links = [
                NavbarLinkData(
                    id="login",
                    label="Login",
                    href="/auth/login",
                    icon="login",
                    order=0,
                    is_active=section == "login",
                ),
                NavbarLinkData(
                    id="signup",
                    label="Sign Up",
                    href="/auth/signup",
                    icon="user-plus",
                    order=1,
                    is_active=section == "signup",
                ),
            ]

        ***REMOVED*** Mobile menu configuration
        mobile_menu = {
            "hamburger_icon": "menu",
            "close_icon": "x",
            "show_brand": True,
            "show_search": True,
        }

        ***REMOVED*** Metadata for navbar behavior
        metadata = {
            "sticky": True,
            "transparent_on_home": True,
            "show_search_bar": True,
            "theme": "dark",
            "version": "1.0.0",
            "last_updated": "2024-01-01T00:00:00Z",
        }

        return NavbarData(
            brand=brand,
            primary_links=primary_links,
            secondary_links=secondary_links,
            user_links=user_links,
            mobile_menu=mobile_menu,
            metadata=metadata,
        )

    except BackendClientError as e:
        logger.error(f"Backend error while fetching navbar content: {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in navbar endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
