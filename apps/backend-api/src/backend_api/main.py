"""
Main FastAPI application for the Next Watch backend API.
"""

import logging
import datetime
import traceback
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, text

***REMOVED*** Import routes
from backend_api.routes import movies, genres

***REMOVED*** Import database initialization
from backend_api.db.database import init_database, get_db

***REMOVED*** Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

***REMOVED*** Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

***REMOVED*** Create FastAPI application
app = FastAPI(
    title="Next Watch API",
    description="API for serving movie data",
    version="0.1.0",
    debug=DEBUG,
)

***REMOVED*** Parse CORS origins
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
cors_origins = (
    [origin.strip() for origin in cors_origins_str.split(",")]
    if cors_origins_str != "*"
    else ["*"]
)

***REMOVED*** Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

***REMOVED*** Register routers
app.include_router(movies.router)
app.include_router(genres.router)

***REMOVED*** Performance metrics middleware if enabled
if os.getenv("ENABLE_PERFORMANCE_METRICS", "false").lower() == "true":

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
    return {
        "time": datetime.datetime.now().isoformat(),
        "client": request.client.host if request.client else None,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": request.path_params,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend_api.main:app", host="0.0.0.0", port=8000, reload=True)
