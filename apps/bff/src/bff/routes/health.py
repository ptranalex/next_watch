"""Health check routes for BFF service."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import time

from bff.config import Config
from bff.config.app import get_config

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: float
    version: str
    environment: str
    backend_api_url: str


@router.get("/", response_model=HealthResponse)
async def health_check(config: Config = Depends(get_config)) -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        Health status information
    """
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="0.1.0",
        environment=config.environment,
        backend_api_url=config.backend_api_url,
    )


@router.get("/ready")
async def readiness_check(config: Config = Depends(get_config)) -> Dict[str, Any]:
    """Readiness check for Kubernetes/Docker.

    Returns:
        Readiness status
    """
    ***REMOVED*** TODO: Add checks for backend API connectivity, Redis, etc.
    return {
        "status": "ready",
        "timestamp": time.time(),
        "checks": {
            "backend_api": "unknown",  ***REMOVED*** Implement actual check
            "redis": "unknown",  ***REMOVED*** Implement actual check
        },
    }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes/Docker.

    Returns:
        Basic liveness confirmation
    """
    return {"status": "alive"}
