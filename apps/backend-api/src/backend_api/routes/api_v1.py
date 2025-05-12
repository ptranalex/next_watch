"""
API v1 router - aggregates and organizes all v1 API endpoints.
"""

from fastapi import APIRouter

***REMOVED*** Import v1 route modules
from backend_api.routes.v1 import (
    movies,
    genres,
    actors,
    search,
    auth,
    user_interactions,
    health,
)

***REMOVED*** Create the v1 API router
api_v1_router = APIRouter(prefix="/api/v1")

***REMOVED*** Include sub-routers
api_v1_router.include_router(movies.router)
api_v1_router.include_router(genres.router)
api_v1_router.include_router(actors.router)
api_v1_router.include_router(search.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(user_interactions.router)
api_v1_router.include_router(health.router)
