"""
Main FastAPI application for the Next Watch Authentication Service.

Dedicated microservice for authentication and token management.
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

***REMOVED*** Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** Load environment variables
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find the .env.local file
        possible_paths = [
            Path(__file__).resolve().parents[3] / ".env.local",
            Path.cwd() / ".env.local",
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Loading environment variables from {path}")
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Import configuration after environment variables are loaded
from auth_api.config.app import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, text
from auth_api.routes.auth import router as auth_router
from auth_api.db.database import init_database, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    ***REMOVED*** Startup
    logger.info("Starting Next Watch Authentication Service")
    logger.info(f"Configuration: {settings}")

    ***REMOVED*** Initialize database
    try:
        init_database()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Next Watch Authentication Service")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create FastAPI app
    app = FastAPI(
        title="Next Watch Authentication API",
        description="Dedicated authentication service for Next Watch movie platform",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  ***REMOVED*** Frontend
            "http://localhost:8001",  ***REMOVED*** BFF
            "http://localhost:8002",  ***REMOVED*** Backend API
        ]
        + settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization", "Content-Type"],
    )

    ***REMOVED*** Add trusted host middleware in production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "auth-api"],
        )

    ***REMOVED*** Register authentication routes
    app.include_router(auth_router)

    ***REMOVED*** Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    return app


***REMOVED*** Create application instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint returning authentication API information."""
    return {
        "service": "Next Watch Authentication API",
        "version": "0.1.0",
        "endpoints": {
            "auth": "Available at /auth/",
        },
        "documentation": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "service": "auth-api",
        "version": "0.1.0",
    }


@app.get("/health/db")
async def db_health_check():
    """Database health check endpoint."""
    try:
        ***REMOVED*** Get a database session
        db_gen = get_db()
        db = next(db_gen)

        ***REMOVED*** Try a simple query
        result = db.execute(text("SELECT 1")).scalar()

        ***REMOVED*** Close the session
        try:
            next(db_gen)
        except StopIteration:
            pass

        return {
            "status": "ok",
            "database": "connected",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "disconnected",
                "error": str(e),
            },
        )
