"""
BFF API v1 router - aggregates and organizes all v1 API endpoints.
"""

from fastapi import APIRouter

***REMOVED*** Import v1 route modules from v1 package
from bff_api.routes.v1 import (
    actors,
    auth,
    genres,
    home,
    liked,
    movies,
    search,
    sidebar,
    top,
    user_interactions,
    watched,
    watchlist,
)

***REMOVED*** Create the v1 API router
api_v1_router = APIRouter(prefix="/bff/v1")

***REMOVED*** Include sub-routers
api_v1_router.include_router(home.router, tags=["home"])
api_v1_router.include_router(movies.router, tags=["movies"])
api_v1_router.include_router(genres.router, tags=["genres"])
api_v1_router.include_router(search.router, tags=["search"])
api_v1_router.include_router(user_interactions.router, tags=["user_interactions"])
api_v1_router.include_router(auth.router, tags=["auth"])
api_v1_router.include_router(sidebar.router, tags=["sidebar"])
api_v1_router.include_router(actors.router, tags=["actors"])
api_v1_router.include_router(top.router, tags=["top"])
api_v1_router.include_router(watched.router, tags=["watched"])
api_v1_router.include_router(watchlist.router, tags=["watchlist"])
api_v1_router.include_router(liked.router, tags=["liked"])
