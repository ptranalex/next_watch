"""Admin-only endpoints for internal monitoring and operations.

These endpoints are intended for internal use only and should not be exposed
to public traffic. They provide operational insights and administrative
functionality for the BFF API service.
"""

from fastapi import APIRouter

# Import admin route modules
from .cache_admin import router as cache_admin_router

# Create admin router with clear prefix
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    include_in_schema=False,  # Hide from public OpenAPI docs
)

# Include admin sub-routers
admin_router.include_router(cache_admin_router, prefix="/cache", tags=["cache-admin"])

__all__ = ["admin_router"]
