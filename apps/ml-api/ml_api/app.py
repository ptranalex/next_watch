"""Main FastAPI application for the ML API."""

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ml_api import __version__
from ml_api.routes import embeddings_router
from ml_api.services import embedding_service

***REMOVED*** Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting ML API")

    ***REMOVED*** Try to load the model, but don't fail if it doesn't work
    ***REMOVED*** The service will use mock embeddings if the model fails to load
    try:
        embedding_service.load_model()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")

    yield

    ***REMOVED*** Shutdown logic can be added here if needed
    logger.info("Shutting down ML API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ML API",
        description="API for machine learning operations for the Next Watch platform",
        version=__version__,
        lifespan=lifespan,
    )

    ***REMOVED*** Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  ***REMOVED*** In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ***REMOVED*** Add TrustedHostMiddleware in production
    if os.getenv("ENVIRONMENT") == "production":
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        allowed_hosts_list = [host.strip() for host in allowed_hosts.split(",")]
        logger.info(f"Adding TrustedHostMiddleware with allowed_hosts: {allowed_hosts_list}")

        from fastapi.middleware.trustedhost import TrustedHostMiddleware

        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts_list,
        )

    ***REMOVED*** Include routers
    app.include_router(embeddings_router)

    ***REMOVED*** Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> Dict[str, str]:
        """Check the health of the API."""
        return {"status": "ok", "version": __version__}

    ***REMOVED*** Add ping endpoint
    @app.get("/ping", tags=["health"])
    async def ping() -> Dict[str, str]:
        """Simple ping endpoint."""
        return {"ping": "pong"}

    ***REMOVED*** Add model health check endpoint
    @app.get("/health/model", tags=["health"])
    async def model_health_check() -> Dict[str, Any]:
        """Check the health of the embedding model."""
        model_info = embedding_service.get_model_info()

        if model_info["health"] != "ok":
            raise HTTPException(
                status_code=503,
                detail=f"Model health is {model_info['health']}",
            )

        return {
            "status": "ok",
            "model": {
                "id": model_info["model_id"],
                "status": model_info["status"],
                "health": model_info["health"],
            },
        }

    return app


app = create_app()

if __name__ == "__main__":
    ***REMOVED*** Get environment variables or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))  ***REMOVED*** Updated to use Docker best practice port 8000
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    ***REMOVED*** Run the application with uvicorn
    logger.info(f"Starting ML API server at http://{host}:{port}")
    uvicorn.run("ml_api.app:app", host=host, port=port, log_level=log_level)
