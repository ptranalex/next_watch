"""
API v1 router - aggregates and organizes all v1 API endpoints.
"""

from fastapi import APIRouter

# Import v1 route modules
from backend_api.routes.v1 import (
    actors,
    genres,
    movies,
    search,
    user_collections,
)

# Create the v1 API router
api_v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_v1_router.include_router(movies.router, tags=["movies"])
api_v1_router.include_router(genres.router, tags=["genres"])
api_v1_router.include_router(actors.router, tags=["actors"])
api_v1_router.include_router(search.router, tags=["search"])
api_v1_router.include_router(user_collections.router, tags=["user_collections"])
