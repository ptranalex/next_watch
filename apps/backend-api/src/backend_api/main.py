"""
Main FastAPI application for the Next Watch backend API.
"""

import os
import sys
from pathlib import Path
import logging

***REMOVED*** Setup basic logging
logging.basicConfig(level=logging.INFO)

***REMOVED*** Load environment variables
try:
    from dotenv import load_dotenv

    ***REMOVED*** Try multiple locations to find the .env.local file
    possible_paths = [
        Path(__file__).resolve().parents[3]
        / ".env.local",  ***REMOVED*** /Users/alex/Sandbox/next_watch/apps/backend-api/.env.local
        Path.cwd() / ".env.local",  ***REMOVED*** Current working directory
    ]

    for path in possible_paths:
        if path.exists():
            load_dotenv(dotenv_path=path, override=True)
            break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Import configuration
from backend_api.config.app import settings

***REMOVED*** Import remaining dependencies
import datetime
import traceback
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, text

***REMOVED*** Import routes
from backend_api.routes import movies, genres, cast

***REMOVED*** Import database initialization
from backend_api.db.database import init_database, get_db

***REMOVED*** Get logger for this module
logger = logging.getLogger(__name__)

***REMOVED*** Create FastAPI application
app = FastAPI(
    title="Next Watch API",
    description="API for serving movie data",
    version="0.1.0",
    debug=settings.debug,
)

***REMOVED*** Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

***REMOVED*** Register routers
app.include_router(movies.router)
app.include_router(genres.router)
app.include_router(cast.router)

***REMOVED*** Performance metrics middleware if enabled
if settings.enable_performance_metrics:

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = datetime.datetime.now()
        response = await call_next(request)
        process_time = (datetime.datetime.now() - start_time).total_seconds()
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(f"Request to {request.url.path} took {process_time:.4f} seconds")
        return response


@app.on_event("startup")
def on_startup():
    """Initialize database on application startup."""
    logger.info("Initializing database connection")
    try:
        init_database()
        logger.info("Database connection established successfully")
        logger.debug(f"Using database URL: {settings}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {"message": "Welcome to Next Watch API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.get("/db-health")
async def db_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint."""
    try:
        ***REMOVED*** Try a simple query
        result = db.execute(text("SELECT 1")).scalar()

        ***REMOVED*** Return success if query worked
        return {
            "status": "ok",
            "result": result,
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


@app.get("/debug")
async def debug_info(request: Request):
    """Debug endpoint returning server information."""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Debug mode disabled")

    return {
        "time": datetime.datetime.now().isoformat(),
        "client": request.client.host if request.client else None,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": request.path_params,
        "settings": str(settings),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend_api.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.debug,
    )
