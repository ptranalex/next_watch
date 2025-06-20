"""API v1 router configuration."""

from fastapi import APIRouter

from recommendation_api.routes.v1 import (
    trending_router,
    popular_router,
    personalized_router,
    similar_router,
)

***REMOVED*** Create the main API v1 router
api_v1_router = APIRouter(prefix="/v1")

***REMOVED*** Include all v1 route modules
api_v1_router.include_router(trending_router)
api_v1_router.include_router(popular_router)
api_v1_router.include_router(personalized_router)
api_v1_router.include_router(similar_router)
