"""Main entry point for running the BFF API server."""

import logging
import os
import sys

import uvicorn

from bff_api.config.app import settings
from bff_api.config.logging import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Run the BFF API server."""
    logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

    try:
        ***REMOVED*** Log that we're starting the server
        logger.info(f"Starting BFF API server on http://{settings.host}:{settings.port}")
        logger.info(f"Debug mode: {settings.debug}")

        ***REMOVED*** Run the server
        uvicorn.run(
            "bff_api.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Failed to start BFF API server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
