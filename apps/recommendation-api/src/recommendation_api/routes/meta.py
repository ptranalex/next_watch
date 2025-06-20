"""Meta routes for the Recommendation API."""

from typing import Dict, Any
from fastapi import APIRouter

from config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to Next Watch Recommendation API",
        "api_versions": {
            "v1": "Available at /v1/recommendations/",
        },
        "health_checks": {
            "comprehensive": "/health - Full health check with all dependencies",
            "liveness": "/health/live - Simple liveness check",
            "readiness": "/health/ready - Readiness check for critical dependencies",
        },
        "documentation": "/docs",
    }
