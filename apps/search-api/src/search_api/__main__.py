"""Entry point for running Search API as a module.

This allows running the service with: python -m search_api
"""

import uvicorn
from search_api.config.app import settings


def main() -> None:
    """Run the Search API server."""
    uvicorn.run(
        "search_api.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
