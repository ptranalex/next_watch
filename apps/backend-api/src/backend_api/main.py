"""
Main FastAPI application for the Next Watch backend API.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

***REMOVED*** Load environment variables first
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find the .env.local file
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd() / ".env.local",
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[3]
            / ".env.local",  ***REMOVED*** /Users/alex/Sandbox/next_watch/apps/backend-api/.env.local
        ]

        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Import configuration after environment variables are loaded
from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

***REMOVED*** Configure logging early
configure_logging(
    log_level=getattr(settings, "log_level", "INFO"),
    log_dir=(
        Path(getattr(settings, "log_dir", "./logs")) if hasattr(settings, "log_dir") else None
    ),
    verbose=settings.debug,
    quiet=False,
)

***REMOVED*** Get logger for this module
logger = get_logger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Import remaining dependencies
import datetime
import traceback

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, text

***REMOVED*** Import database initialization
from backend_api.db.database import get_db, init_database

***REMOVED*** Import middlewares
from backend_api.middlewares import ErrorHandlerMiddleware

***REMOVED*** Import versioned API router
from backend_api.routes.api_v1 import api_v1_router

***REMOVED*** Import services
try:
    from backend_api.services.suggestion_engine import SuggestionEngine

    suggestion_service_enabled = True
except ImportError:
    suggestion_service_enabled = False
    logger.warning("Redis suggestion engine not available: redis-py not installed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown of the FastAPI application including
    database initialization and suggestion engine setup.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting Backend API service")

    ***REMOVED*** Initialize database
    logger.info("Initializing database connection")
    try:
        init_database()
        logger.info("Database connection established successfully")
        logger.debug(f"Using database URL: {settings}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    ***REMOVED*** Initialize suggestion engine
    suggestion_engine = None
    if suggestion_service_enabled:
        try:
            ***REMOVED*** Get Redis URL from environment or use default
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            logger.info(f"Initializing Redis suggestion engine with URL: {redis_url}")

            suggestion_engine = SuggestionEngine(redis_url)
            await suggestion_engine.initialize()
            app.state.suggestion_engine = suggestion_engine

            logger.info("Redis suggestion engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis suggestion engine: {e}")
            logger.error(traceback.format_exc())
            ***REMOVED*** Don't raise - application should still start without suggestion service
    else:
        logger.warning("Suggestion service not enabled - Redis dependencies missing")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Backend API service")
    if hasattr(app.state, "suggestion_engine") and app.state.suggestion_engine is not None:
        try:
            logger.info("Shutting down Redis suggestion engine")
            await app.state.suggestion_engine.shutdown()
            logger.info("Redis suggestion engine shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down Redis suggestion engine: {e}")
            logger.error(traceback.format_exc())


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application with all middleware and routes
    """
    ***REMOVED*** Create FastAPI application
    app = FastAPI(
        title="Next Watch API",
        description="API for serving movie data",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  ***REMOVED*** Default Next.js port
            "http://localhost:3001",  ***REMOVED*** Your current port
            "http://localhost:3002",  ***REMOVED*** Any other ports you might use
            "http://localhost:8000",  ***REMOVED*** Other common development ports
            "http://127.0.0.1:3000",  ***REMOVED*** Also allow 127.0.0.1
            "http://127.0.0.1:3001",
        ]
        + settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization", "Content-Type"],
    )

    ***REMOVED*** Add error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)

    ***REMOVED*** Performance metrics middleware if enabled
    if settings.enable_performance_metrics:

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            """Add performance timing header to responses.

            Args:
                request: FastAPI request object
                call_next: Next middleware in chain

            Returns:
                Response with X-Process-Time header added
            """
            start_time = datetime.datetime.now()
            response = await call_next(request)
            process_time = (datetime.datetime.now() - start_time).total_seconds()
            response.headers["X-Process-Time"] = str(process_time)
            logger.debug(f"Request to {request.url.path} took {process_time:.4f} seconds")
            return response

    ***REMOVED*** Register v1 API router - this is the new, organized API
    app.include_router(api_v1_router)

    ***REMOVED*** Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions globally.

        Args:
            request: FastAPI request object
            exc: Exception that was raised

        Returns:
            JSON error response
        """
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


***REMOVED*** Create default app instance
app = create_app()


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning API information.

    Returns:
        API information including available versions and documentation links
    """
    return {
        "message": "Welcome to Next Watch API",
        "api_versions": {
            "v1": "Available at /api/v1/",
        },
        "documentation": "/docs",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring.

    Returns:
        Health status information
    """
    return {"status": "ok"}


@app.get("/db-health")
async def db_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Database health check endpoint.

    Args:
        db: Database session dependency

    Returns:
        Database health status and connection information
    """
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
async def debug_info(request: Request) -> Dict[str, Any]:
    """Debug endpoint returning server information.

    Args:
        request: FastAPI request object

    Returns:
        Debug information including request details and server settings

    Raises:
        HTTPException: If debug mode is disabled
    """
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
