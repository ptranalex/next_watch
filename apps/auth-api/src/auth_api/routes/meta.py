"""Meta routes for basic API information and health checks."""

import logging
from typing import Any, Dict, Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import text

from auth_api.db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning authentication API information.

    Returns:
        API information including available endpoints and documentation links
    """
    return {
        "service": "Next Watch Authentication API",
        "version": "0.1.0",
        "endpoints": {
            "auth": "Available at /auth/",
        },
        "documentation": "/docs",
    }
