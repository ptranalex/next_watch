"""
Search API v1 router - aggregates and organizes all v1 API endpoints.
"""

from fastapi import APIRouter

# Import v1 route modules from v1 package
from search_api.routes.v1 import (
    search,
    suggestions,
)

# Create the v1 API router
api_v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_v1_router.include_router(search.router, tags=["search"])
api_v1_router.include_router(suggestions.router, tags=["suggestions"])
