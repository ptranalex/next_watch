"""
BFF API v1 router - aggregates and organizes all v1 API endpoints.
"""

from fastapi import APIRouter

***REMOVED*** Import v1 route modules from v1 package
from bff_api.routes.v1 import (
    home,
    movies,
    genres,
    search,
    user_interactions,
    auth,
    health,
    navbar,
    sidebar,
    actors,
    top,
    watched,
    watchlist,
    liked,
)

***REMOVED*** Create the v1 API router
api_v1_router = APIRouter(prefix="/v1")

***REMOVED*** Include sub-routers
api_v1_router.include_router(home.router)
api_v1_router.include_router(movies.router)
api_v1_router.include_router(genres.router)
api_v1_router.include_router(search.router)
api_v1_router.include_router(user_interactions.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(health.router)
api_v1_router.include_router(navbar.router)
api_v1_router.include_router(sidebar.router)
api_v1_router.include_router(actors.router)
api_v1_router.include_router(top.router)
api_v1_router.include_router(watched.router)
api_v1_router.include_router(watchlist.router)
api_v1_router.include_router(liked.router)
