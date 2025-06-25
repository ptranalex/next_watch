"""
Auth API v1 router - organizes all v1 API endpoints.
"""

from fastapi import APIRouter

***REMOVED*** Import v1 route modules
from auth_api.routes.v1 import auth, users

***REMOVED*** Create the v1 API router
api_v1_router = APIRouter(prefix="/auth/v1")

***REMOVED*** Include sub-routers
api_v1_router.include_router(auth.router, tags=["authentication"])
api_v1_router.include_router(users.router, tags=["users"])
