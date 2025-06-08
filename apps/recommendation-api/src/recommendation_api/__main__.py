"""Main entry point for the Recommendation API.

This module allows running the API with `python -m recommendation_api`.
"""

import sys
import uvicorn

from recommendation_api.config.app import settings


def main() -> None:
    """Run the Recommendation API server."""
    uvicorn.run(
        "recommendation_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
        proxy_headers=settings.proxy_headers,
        forwarded_allow_ips=settings.forwarded_allow_ips,
    )


if __name__ == "__main__":
    main()
