"""Main entry point for running the BFF API server."""

import os
import sys

import uvicorn
from config.logging import get_logger

from bff_api.config.app import settings

logger = get_logger(__name__)


def main() -> None:
    """Run the BFF API server."""
    logger.info(f"Running in environment: {settings.environment}")

    ***REMOVED*** Infrastructure parameters from environment (deployment concerns)
    workers = int(os.getenv("WORKERS", "1"))
    timeout_keep_alive = int(os.getenv("TIMEOUT", "120"))
    limit_max_requests = int(os.getenv("LIMIT_MAX_REQUESTS", "1000"))
    backlog = int(os.getenv("BACKLOG", "1024"))
    forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")

    try:
        ***REMOVED*** Log that we're starting the server
        logger.info(f"Starting BFF API server on http://{settings.host}:{settings.port}")
        logger.info(f"Debug mode: {settings.debug}")

        if not settings.debug:
            logger.info(
                f"Production config: workers={workers}, timeout={timeout_keep_alive}s, backlog={backlog}"
            )

        ***REMOVED*** Run the server with appropriate configuration
        if settings.debug:
            ***REMOVED*** Development: Single worker with reload
            uvicorn.run(
                app="bff_api.main:create_app",
                factory=True,
                host=settings.host,
                port=settings.port,
                log_level=settings.log_level.lower(),
                reload=True,
                access_log=True,
            )
        else:
            ***REMOVED*** Production: Multiple workers with optimizations
            uvicorn.run(
                app="bff_api.main:create_app",
                factory=True,
                host=settings.host,
                port=settings.port,
                log_level=settings.log_level.lower(),
                workers=workers,
                timeout_keep_alive=timeout_keep_alive,
                limit_max_requests=limit_max_requests,
                backlog=backlog,
                access_log=False,  ***REMOVED*** Disable access logs for performance
                proxy_headers=True,
                forwarded_allow_ips=forwarded_allow_ips,
            )

    except Exception as e:
        logger.error(f"Failed to start BFF API server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
