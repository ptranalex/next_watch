"""
Health check endpoints for monitoring the API.
"""

import datetime
import logging
import traceback

from fastapi import APIRouter, Depends
from sqlmodel import Session, text

from backend_api.db.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

***REMOVED*** Get logger for this module
logger = logging.getLogger(__name__)


@router.get("", summary="Basic health check")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@router.get("/db", summary="Database health check")
async def db_health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Database health check endpoint."""
    try:
        ***REMOVED*** Try a simple query
        result = db.execute(text("SELECT 1")).scalar()

        ***REMOVED*** Return success if query worked
        return {
            "status": "ok",
            "result": str(result) if result else "",
            "db_type": str(type(db)),
            "timestamp": datetime.datetime.now().isoformat(),
        }
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Database health check failed: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        return {
            "status": "error",
            "error": str(e),
            "trace": stack_trace,
            "timestamp": datetime.datetime.now().isoformat(),
        }
