"""Home screen routes for BFF API."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.schemas.screen_schemas import HomeScreenData
from bff_api.dependencies.common import get_backend_client
from bff_api.services.backend_client import BackendClient, BackendClientError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["home"])


@router.get("/home", response_model=HomeScreenData)
async def get_home_screen(
    user_id: Optional[int] = Query(
        None, description="User ID for personalized content"
    ),
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
        HTTPException: If backend service is unavailable (502)
    """
    try:
        ***REMOVED*** Fetch data concurrently (in real implementation, use asyncio.gather)
        featured_movies_response = await backend.get_movies(
            page=1, limit=10, featured=True, user_id=user_id
        )
        popular_movies_response = await backend.get_movies(
            page=1, limit=20, sort="popularity", user_id=user_id
        )
        recent_releases_response = await backend.get_movies(
            page=1, limit=15, sort="release_date", user_id=user_id
        )
        genres = await backend.get_genres()

        ***REMOVED*** Handle user recommendations
        user_recommendations = []
        if user_id:
            try:
                recommendations_response = await backend.get_movies(
                    page=1, limit=20, recommended_for=user_id, user_id=user_id
                )
                user_recommendations = recommendations_response.get("results", [])
            except BackendClientError:
                logger.warning(f"Failed to get recommendations for user {user_id}")

        return HomeScreenData(
            featured_movies=featured_movies_response.get("results", []),
            popular_movies=popular_movies_response.get("results", []),
            recent_releases=recent_releases_response.get("results", []),
            user_recommendations=user_recommendations,
            genres=genres,
        )

    except BackendClientError as e:
        logger.error(f"Backend error in home screen: {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable") 