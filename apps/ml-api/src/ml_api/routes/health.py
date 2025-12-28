"""Health check routes for ML API."""

from __future__ import annotations

from typing import Any

from config.logging import get_logger
from fastapi import APIRouter, HTTPException

from ml_api import __version__
from ml_api.services import embedding_service

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Check the health of the API."""
    return {"status": "ok", "version": __version__}


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Simple ping endpoint."""
    return {"ping": "pong"}


@router.get("/health/model")
async def model_health_check() -> dict[str, Any]:
    """Check the health of the embedding model."""
    try:
        model_info = embedding_service.get_model_info()

        if model_info["health"] != "ok":
            raise HTTPException(status_code=503, detail=f"Model health is {model_info['health']}")

        return {
            "status": "ok",
            "model": {
                "id": model_info["model_id"],
                "status": model_info["status"],
                "health": model_info["health"],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking model health: {e}")
        raise HTTPException(status_code=503, detail=f"Model health check failed: {e!s}") from e
